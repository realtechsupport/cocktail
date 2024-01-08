import os
import rasterio
from rasterio.mask import mask
import geopandas as gpd
from shapely.geometry import mapping
import tensorflow as tf
import glob
from google.cloud import storage

# Specify the folder path where your images are located
folder_path = '/Users/srikarreddy/Desktop/satellite_imagery/images/'

# Specify the folder path where your labels are located
label_folder = '/Users/srikarreddy/Desktop/satellite_imagery/label/'

#Specify the path where your clipping mask are located
geojson_datapath = '/Users/srikarreddy/Desktop/satellite_imagery/label/newextent_1123.geojson'

# Specify the GCS bucket name
bucket_name = 'dummy-srikar-bucket'

# Specify the GCS path for TFRecords
gcs_output_dir = f'gs://{bucket_name}/tf_records/'

def create_gcs_bucket(bucket_name):
    # Create a GCS client
    client = storage.Client()

    # Create a GCS bucket
    bucket = client.bucket(bucket_name)
    if not bucket.exists():
        bucket.create()


def clip_tiff(tiff, geojson = geojson_datapath):

    with open(geojson) as clip_geojson:
        clip_geojson = gpd.read_file(clip_geojson)
        clip_geometry = clip_geojson.geometry.values[0]
        clip_geojson = mapping(clip_geometry)

    with rasterio.open(tiff) as src:
        # Perform the clip
        clip_image, clip_transform = mask(src, [clip_geojson], crop=True)

    return clip_image

# preprocessing functions

def resize_img(image,label):
  image = tf.image.resize_with_crop_or_pad(image, label.shape[0], label.shape[1])
  return image, label


def process_input(image, label):

    tensor_image = tf.convert_to_tensor(image)
    tensor_image = tf.transpose(tensor_image, perm=[1, 2, 0])
    tensor_label = tf.convert_to_tensor(label)
    tensor_label = tf.transpose(tensor_label, perm=[1, 2, 0])

    if tensor_label.shape[:2] != tensor_image.shape[:2]:
      tensor_image, tensor_label = resize_img(tensor_image, tensor_label)

    return tensor_image, tensor_label


def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=value))


def _float_feature(value):
    return tf.train.Feature(float_list=tf.train.FloatList(value=value))

def create_tfrecord(image, label):
    image = clip_tiff(image)
    label = clip_tiff(label)
    image, label = process_input(image, label)
    image_dims = image.shape
    label_dims = label.shape

    image = tf.reshape(image, [-1])  # flatten to 1D array
    label = tf.reshape(label, [-1])  # flatten to 1D array

    return tf.train.Example(
        features=tf.train.Features(
            feature={
                "image": _float_feature(image.numpy()),
                "image_shape": _int64_feature(
                    [image_dims[0], image_dims[1], image_dims[2]]
                ),
                "label": _float_feature(label.numpy()),
                "label_shape": _int64_feature([label_dims[0], label_dims[1], label_dims[2]]),
            }
        )
    ).SerializeToString()

def write_tfrecords(images, labels, gcs_output_directory):
    create_gcs_bucket(bucket_name)

    for image, label in zip(images, labels):
        # Create GCS path for TFRecord
        output_file_gcs = os.path.join(gcs_output_directory, f"{image.replace(folder_path,'').replace('.tif','')}_tfrecord.tfrecord")

        # Open a GCS file for writing
        with tf.io.gfile.GFile(output_file_gcs, 'wb') as gcs_writer:
            tf_example = create_tfrecord(image, label)
            gcs_writer.write(tf_example)

if __name__ == "__main__":
    images = glob.glob(folder_path + '*.tif')  # list of file locations of all images
    number_of_images = len(images)
    labels = glob.glob(label_folder + '*.tif')
    labels = labels * number_of_images

    write_tfrecords(images, labels, gcs_output_dir)
