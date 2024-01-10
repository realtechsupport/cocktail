# imports================

import os
from tensorflow import keras
from tensorflow.keras import layers
import tensorflow as tf
from google.cloud import storage
from trainer.model_file import get_model

# Necessary Functions------------------------------------------

feature_description = {
    "image": tf.io.VarLenFeature(tf.float32),
    "image_shape": tf.io.VarLenFeature(tf.int64),
    "label": tf.io.VarLenFeature(tf.float32),
    "label_shape": tf.io.VarLenFeature(tf.int64),
}


def parse(serialized_examples):
    return tf.io.parse_example(serialized_examples, feature_description)


def create_dataset(input_directory):
    tfrecord_files = [
        f"{input_directory}{file}"
        for file in tf.io.gfile.listdir(input_directory)
        if file.endswith(".tfrecord")
    ]
    dataset = tf.data.TFRecordDataset(tfrecord_files)
    dataset = dataset.map(parse)
    return dataset


# pre-processing functions
def bandwise_normalize(input_tensor, epsilon=1e-8):
    # Convert the input_tensor to a float32 type
    input_tensor = tf.cast(input_tensor, tf.float32)

    # Calculate the minimum and maximum values along the channel axis
    min_val = tf.reduce_min(input_tensor, axis=2, keepdims=True)
    max_val = tf.reduce_max(input_tensor, axis=2, keepdims=True)

    # Check for potential numerical instability
    denom = max_val - min_val
    denom = tf.where(tf.abs(denom) < epsilon, epsilon, denom)

    # Normalize the tensor band-wise to the range [0, 1]
    normalized_tensor = (input_tensor - min_val) / denom

    return normalized_tensor


def pad_to_multiple(image, TILE_HT, TILE_WD):
    # Get the current dimensions
    height, width, channels = image.shape

    # Calculate the target dimensions
    target_height = tf.cast(tf.math.ceil(height / TILE_HT) * TILE_HT, tf.int32)
    target_width = tf.cast(tf.math.ceil(width / TILE_WD) * TILE_WD, tf.int32)

    # Calculate the amount of padding
    pad_height = target_height - height
    pad_width = target_width - width

    # Pad the image
    padded_image = tf.image.resize_with_crop_or_pad(image, target_height, target_width)

    return padded_image


def tile_image(fullimg, CHANNELS, TILE_HT, TILE_WD):
    fullimg = pad_to_multiple(fullimg, TILE_HT, TILE_WD)
    images = tf.expand_dims(fullimg, axis=0)
    tiles = tf.image.extract_patches(
        images=images,
        sizes=[1, TILE_HT, TILE_WD, 1],
        strides=[1, TILE_HT, TILE_WD, 1],
        rates=[1, 1, 1, 1],
        padding="VALID",
    )

    tiles = tf.squeeze(tiles, axis=0)
    nrows = tiles.shape[0]
    ncols = tiles.shape[1]
    tiles = tf.reshape(tiles, [nrows, ncols, TILE_HT, TILE_WD, CHANNELS])
    return tiles


def sampling(label_image, threshold_percentage=99.9):
    num_zeros = tf.reduce_sum(
        tf.cast(tf.equal(label_image, 0), tf.float32), axis=[2, 3, 4]
    )

    # Calculate the total number of elements in each patch
    total_elements = tf.cast(tf.reduce_prod(tf.shape(label_image)[2:]), tf.float32)

    # Calculate the percentage of zeros in each patch
    percentage_zeros = (num_zeros / total_elements) * 100.0

    boolean_mask = percentage_zeros <= threshold_percentage
    # Apply the threshold logic
    sampled_tensor = tf.cast(percentage_zeros >= threshold_percentage, tf.int32)
    return boolean_mask, sampled_tensor


def one_hot_encoding(label_tensor):
    # Assuming your pixel values are float labels
    float_labels = tf.squeeze(
        label_tensor, axis=-1
    )  # Assuming channel dimension is the last one

    # Determine the number of classes dynamically
    num_classes = tf.cast(tf.reduce_max(float_labels) + 1, tf.int32)

    # One-hot encode each image
    one_hot_encoded_images = tf.one_hot(
        tf.dtypes.cast(float_labels, tf.int32), depth=num_classes
    )

    # Print the shape of the resulting tensor and the number of classes
    # print("Shape of one-hot encoded images:", one_hot_encoded_images.shape)
    # print("Number of classes:", num_classes)

    return one_hot_encoded_images


def parsing(
    dataset,
    patch_height,
    patch_width,
    threshold_percentage,
    image_channels,
    label_channels,
):
    image_patch_tensors_list = []
    label_patch_tensors_list = []

    for parsed_example in dataset:
        image_shape = tf.sparse.to_dense(parsed_example["image_shape"])
        image = tf.reshape(tf.sparse.to_dense(parsed_example["image"]), image_shape)
        label_shape = tf.sparse.to_dense(parsed_example["label_shape"])
        label = tf.reshape(tf.sparse.to_dense(parsed_example["label"]), label_shape)

        # image normalization
        image = bandwise_normalize(image)

        # image and label patching
        image_patches = tile_image(image, image_channels, patch_height, patch_width)
        label_patches = tile_image(label, label_channels, patch_height, patch_width)

        # sampling
        sampled_mask, sampled_tensor = sampling(label_patches, threshold_percentage)
        sampled_image_patches = tf.boolean_mask(image_patches, sampled_mask)
        sampled_label_patches = tf.boolean_mask(label_patches, sampled_mask)

        # one-hot encoding
        sampled_label_patches = one_hot_encoding(sampled_label_patches)

        # save them in the list
        image_patch_tensors_list.append(sampled_image_patches)
        label_patch_tensors_list.append(sampled_label_patches)

    return image_patch_tensors_list, label_patch_tensors_list


def train_test_datasets(
    input_directory,
    patch_height,
    patch_width,
    image_channels,
    label_channels,
    threshold_percentage,
    batch_size,
):
    dataset = create_dataset(input_directory)
    image_patch_tensors_list, label_patch_tensors_list = parsing(
        dataset=dataset,
        patch_height=patch_height,
        patch_width=patch_width,
        image_channels=image_channels,
        label_channels=label_channels,
        threshold_percentage=threshold_percentage,
    )

    # Combine images and labels from different pairs
    combined_images = tf.concat(image_patch_tensors_list, axis=0)
    combined_labels = tf.concat(label_patch_tensors_list, axis=0)

    # Shuffle the combined data
    combined_dataset = tf.data.Dataset.from_tensor_slices(
        (combined_images, combined_labels)
    )
    combined_dataset = combined_dataset.shuffle(buffer_size=combined_images.shape[0])

    # Split the combined dataset into training and validation sets
    train_size = int(0.8 * combined_images.shape[0])
    train_dataset = combined_dataset.take(train_size)
    val_dataset = combined_dataset.skip(train_size)

    # Batch the data using TensorFlow's Dataset API
    train_dataset = train_dataset.batch(batch_size)
    val_dataset = val_dataset.batch(batch_size)

    return train_dataset, val_dataset





def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client(project="gislogics")
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print("File {} uploaded to {}.".format(source_file_name, destination_blob_name))


# Modeling--------------------------------------------------


def train(**kwargs):
    input_directory = kwargs.get("input_directory")
    threshold_percentage = kwargs.get("threshold_percentage")
    image_channels = kwargs.get("image_channels")
    label_channels = kwargs.get("label_channels")
    patch_height = kwargs.get("patch_height")
    patch_width = kwargs.get("patch_width")
    batch_size = kwargs.get("batch_size")
    num_classes = kwargs.get("num_classes")
    model_path = kwargs.get("model_path")
    bucket_name = kwargs.get("bucket_name")
    img_size = (patch_height, patch_width)
    model_name = f"patch_h{patch_height}_w{patch_width}_batch_{batch_size}.hdf5"

    # get the train and test datasets
    train_dataset, val_dataset = train_test_datasets(
        input_directory,
        patch_height,
        patch_width,
        image_channels,
        label_channels,
        threshold_percentage,
        batch_size,
    )
    print("Train and Valid datasets are created")

    # create img_size
    model = get_model(
        img_size=img_size, num_classes=num_classes, num_bands=image_channels
    )
    model.compile(optimizer="adam", loss="categorical_crossentropy")
    callbacks = [
        keras.callbacks.ModelCheckpoint(model_path + model_name, save_best_only=True),
        keras.callbacks.CSVLogger(input_directory + "logs/" + f"training_logs_{model_name}.csv"),  # Add CSVLogger
    ]
    model_history = model.fit(
        train_dataset,
        epochs=100,
        callbacks=callbacks,
        batch_size=32,
        validation_data=val_dataset,
    )
    model.save(model_path + model_name)
    print("model saved locally")

    upload_blob(bucket_name, model_path + model_name, "model/" + model_name)
    print("uploaded to cloud storage successfully")


if __name__ == "__main__":
    input_params = {
        "input_directory": "gs://tf_records_bucket/tf_records/",  # make sure / is there at the end,
        "bucket_name": "tf_records_bucket",
        "threshold_percentage": 99.9,
        "image_channels": 8,  # 8 bands images as input
        "label_channels": 1,
        "patch_height": 8,
        "patch_width": 8,
        "batch_size": 32,
        "num_classes": 23,
        "model_path": "trained_model/",
    }  # makesure there is a slash at the end of the path  # Choose an appropriate batch size

    train(**input_params)
