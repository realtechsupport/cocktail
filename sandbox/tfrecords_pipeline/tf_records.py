import os
import rasterio
from rasterio.mask import mask
import geopandas as gpd
from shapely.geometry import mapping
import tensorflow as tf
import glob

# Specify the folder path where your images are located
folder_path = '/home/otbuser/all/data/images/'

# Specify the folder path where your labels are located
label_folder = '/home/otbuser/all/data/label/'

#Specify the path where your clipping mask are located
geojson_datapath = '/home/otbuser/all/data/newextent_1123.geojson'

#specify the tf.record path
output_dir = '/home/otbuser/all/data/tf_records/'


def clip_tiff(tiff, geojson):

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

def write_tfrecords(images, labels, output_directory):
    os.makedirs(output_directory, exist_ok=True)
    for image, label in zip(images, labels):
        output_file = os.path.join(output_directory, f"{image.replace(folder_path,'').replace('.tif','')}_tfrecord.tfrecord")
        with tf.io.TFRecordWriter(output_file) as writer:
            tf_example = create_tfrecord(image, label)
            writer.write(tf_example)
    
if __name__=="__main__":
    images = glob.glob(folder_path + '*.tif') #list of filelocations of all images
    number_of_images = len(images)
    labels = glob.glob(label_folder + '*.tif')
    labels = labels*number_of_images

    write_tfrecords(images, labels, output_dir)