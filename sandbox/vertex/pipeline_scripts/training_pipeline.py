import os
from tensorflow import keras
from tensorflow.keras import layers
import tensorflow as tf
from google.cloud import storage
from pipeline_scripts.model_file import get_model
from pipeline_scripts.writing_config import *
import json



### +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def load_config(file_path):
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config


def pretrain():
    # Load configuration
    config = load_config('./pipeline_scripts/config.json')
    # config["img_size"] = config["img_size"]
    model_path = config.get("model_path")
    model_name = config.get("model_name")
    img_size_value = config.get("img_size")
    img_size = (img_size_value, img_size_value)
    num_classes = config.get("num_classes")
    num_bands = config.get("num_bands")
    

    # Create a dummy model
    model = get_model(
        img_size=img_size, 
        num_classes=num_classes, 
        num_bands=num_bands
    )
    model.compile(optimizer="adam", loss="categorical_crossentropy")

    # Save the dummy model
    model.save(model_path)
    print("Dummy model saved at:", model_path)


    # Optionally, you can return the path to the saved dummy model
    return model_path

### ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
pretrain()



import rasterio
from rasterio.mask import mask
import geopandas as gpd
from shapely.geometry import mapping
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping
import time
from tensorflow import keras
from tensorflow.keras.callbacks import TensorBoard
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns
from shapely.geometry import mapping

from pipeline_scripts.prediction import *
from pipeline_scripts.eval import *
from tensorflow.keras.callbacks import Callback
from google.cloud import storage
import os
import csv
from PIL import Image
import io


# metrics_results = compute_metrics(new_ground_truth, new_predict)


# metrics_results

from matplotlib.colors import ListedColormap
class_colors = {
        1: ( 5, 5, 230),
        2: (190, 60, 15),
        3: (65, 240, 125),
        4: (105, 200, 95),
        5: ( 30, 115, 10),
        6: ( 255, 196, 34),
        7: (110, 85, 5),
        8: ( 235, 235, 220),
        9: (120, 216, 47),
        10: ( 84, 142, 128),
        11: ( 84, 142, 128),
        12: ( 84, 142, 128),
        13: ( 50, 255, 215),
        14: ( 50, 255, 215),
        15: ( 50, 255, 215),
        16: ( 193, 255, 0),
        17: ( 105, 200, 95),
        18: (105, 200, 95),
        19: ( 105, 200, 95),
        20: (193, 255, 0),
        21: ( 255, 50, 185),
        22: (255, 255, 255),
}

# Create a colormap using the class-color mapping
colors = [class_colors[i] for i in range(1, 23)]
normalized_colors_array = np.array([tuple(np.array(v) / 255.0) for v in class_colors.values()])

cmap_image = ListedColormap(normalized_colors_array)



class CustomMetricsCSVLogger(Callback):
    def __init__(self, filename, separator=',', append=True):
        super(CustomMetricsCSVLogger, self).__init__()
        self.filename = filename
        self.separator = separator
        self.append = append
        self.keys = None
        self.append_header = True
        self.max_epoch = 0  # Track the highest epoch number encountered
    def on_epoch_begin(self, epoch, logs=None):
        # Initialize min and max class-wise IOU at the beginning of each epoch
        self.min_class_wise_iou = 100
        self.max_class_wise_iou = 0

        # Check if the file exists in Cloud Storage, if not, create it
        if not self.file_exists():
            self.create_file()

    def file_exists(self):
        # Check if the file exists in Cloud Storage
        storage_client = storage.Client()
        bucket_name, blob_name = self.parse_gcs_path(self.filename)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        return blob.exists()

    def create_file(self):
        # Create the file in Cloud Storage and write the header
        storage_client = storage.Client()
        bucket_name, blob_name = self.parse_gcs_path(self.filename)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Write the header to the blob
        header = 'epoch,loss,val_loss,class_wise_iou,class_wise_dice_score,class_wise_accuracy,class_wise_precision,class_wise_recall,mean_iou,min_class_wise_iou,max_class_wise_iou\n'
        blob.upload_from_string(header)

    def parse_gcs_path(self, gcs_path):
        # Parse the Google Cloud Storage path to extract bucket name and blob name
        parts = gcs_path.replace('gs://', '').split('/')
        return parts[0], '/'.join(parts[1:])

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        if self.keys is None:
            self.keys = sorted(logs.keys())

        # Extract class-wise IOU
        class_wise_iou = logs.get('class_wise_iou', 0.0)

        # Update min and max class-wise IOU
        self.min_class_wise_iou = min(self.min_class_wise_iou, class_wise_iou)
        self.max_class_wise_iou = max(self.max_class_wise_iou, class_wise_iou)

        # Append the row to the file in Cloud Storage
        storage_client = storage.Client()
        bucket_name, blob_name = self.parse_gcs_path(self.filename)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Download existing content
        existing_content = blob.download_as_text() if blob.exists() else ""

        # Extract metrics values from logs
        metrics_values = [str(logs[key]) for key in ['loss', 'val_loss', 'class_wise_iou', 'class_wise_dice_score',
                                                    'class_wise_accuracy', 'class_wise_precision', 'class_wise_recall', 'mean_iou']]

        # Check if metrics for the current epoch already exist
        epoch_exists = any(f"{epoch}," in line for line in existing_content.split('\n'))

        # If the file is empty or epoch entry doesn't exist, append the metrics
        if not existing_content or not epoch_exists:
            updated_content = existing_content + f"{epoch},{','.join(metrics_values)},{self.min_class_wise_iou},{self.max_class_wise_iou}\n"
        else:
            # Get the maximum epoch number in the existing content
            max_existing_epoch = max(
                int(line.split(',')[0]) for line in existing_content.split('\n') if line.strip() and not line.startswith('epoch')
            )

            # Increment the epoch for the new entries
            updated_content = existing_content + f"{max_existing_epoch + 1},{','.join(metrics_values)},{self.min_class_wise_iou},{self.max_class_wise_iou}\n"

        # Update the highest epoch number
        self.max_epoch = max(self.max_epoch, epoch)

        # Upload updated content
        blob.upload_from_string(updated_content)





from tensorflow.keras.callbacks import Callback
import matplotlib.pyplot as plt
import os

import io

from datetime import datetime

from google.cloud import storage


class PredictSegmentationCallback(Callback):
    def __init__(self, test_image_path, output_save_path):
        super(PredictSegmentationCallback, self).__init__()
        self.test_image_path = test_image_path
        self.output_save_path = output_save_path  # This variable may contain the full path to the image
        self.last_predicted_array = None
        self.epoch_counter = 0
        self.start_time_str = datetime.now().strftime("%m_%d_%H_%M")  # Changed format for date-time

    def parse_gcs_path(self, gcs_path):
        parts = gcs_path.replace('gs://', '').split('/')
        return parts[0], '/'.join(parts[1:])

    def create_folder_if_not_exists(self, folder_path):
        storage_client = storage.Client()
        bucket_name, folder_blob_name = self.parse_gcs_path(folder_path)
        bucket = storage_client.bucket(bucket_name)  

        # Ensure the folder_blob_name ends with '/'
        if not folder_blob_name.endswith('/'):
            folder_blob_name += '/'

        # Check if the folder already exists
        folder_blob = bucket.blob(folder_blob_name)
        if not folder_blob.exists():
            # Create an empty blob to represent the folder
            folder_blob.upload_from_string('')

    def on_epoch_end(self, epoch, logs=None):
        self.epoch_counter += 1
        if self.epoch_counter % 20 == 0:
            self.last_predicted_array = prediction_function_img(self.test_image_path)
            pil_image = Image.fromarray((self.last_predicted_array * 255).astype(np.uint8))
            pil_image_colored = pil_image.convert('P', palette=Image.ADAPTIVE, colors=len(class_colors))
            pil_image_colored.putpalette(np.array(normalized_colors_array * 255, dtype=np.uint8).flatten())

            # Get the name of the test image without extension
            test_image_name = os.path.splitext(os.path.basename(self.test_image_path))[0]

            # Construct the image name with the start time and epoch
            image_name = f"{self.start_time_str}_epoch_{epoch}.png"

            # Construct the GCS path for saving the image inside the folder
            gcs_content_save_path = os.path.join(self.output_save_path, test_image_name, image_name)

            # Remove the leading 'gs://' and split the path to extract the bucket name
            bucket_name, relative_path = self.parse_gcs_path(gcs_content_save_path)

            # Upload the image to GCS
            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(relative_path)  
            with io.BytesIO() as output:
                pil_image_colored.save(output, format='PNG')
                output.seek(0)
                try:
                    # Convert the output to bytes
                    image_bytes = output.read()

                    # Upload the image bytes to GCS using upload_from_string
                    blob.upload_from_string(image_bytes, content_type='image/png')

                    print(f'Image saved at: {gcs_content_save_path}')

                    # Check if the image exists in GCS
                    if blob.exists():
                        print(f'Image successfully uploaded to GCS: {gcs_content_save_path}')
                    else:
                        print(f'Image not found in GCS after upload: {gcs_content_save_path}')

                except Exception as e:
                    print(f'Error uploading image: {e}')

            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
# imports================

import os
from tensorflow import keras
from tensorflow.keras import layers
import tensorflow as tf
from google.cloud import storage
from pipeline_scripts.model_file import get_model

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
    label_channels = 1
    config = load_config('./pipeline_scripts/config.json')
    # config["img_size"] = tuple(config["img_size"])
    model_path = config.get("model_path")
    model_name = config.get("model_name")
    test_image_path = config.get("test_image_path")
    img_size_value = config.get("img_size")
    img_size = (img_size_value,img_size_value)
    num_bands = config.get("num_bands")
    num_classes = config.get("num_classes")
    gcs_path = config.get("google_storage_path")
    gcs_tfrecords = config.get("gcs_tfrecords")
    class_name = config.get("class_name")
    class_optimization = config.get("class_optmized_model")
    bucket_name = config.get("bucket_name")
    threshold_percentage = config.get("threshold_percentage")
    patch_height = config.get("patch_height")
    patch_width = config.get("patch_width")
    batch_size = config.get("batch_size")
    num_epochs = config.get("epochs")
    
    
    input_directory = gcs_tfrecords
    image_channels = num_bands
    label_channels = 1
    
    

    # get the train and test datasets
    train_dataset, val_dataset = train_test_datasets(
        gcs_tfrecords,
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
        img_size=img_size, 
        num_classes=num_classes, 
        num_bands=image_channels
    )
    
    
    # compilation of model, with custom metric
    # compilation of model, with custom metric
    if class_optimization:
        print("OPTIMIZING BOTH")
        metric = - compute_metrics(new_ground_truth, new_predict)[0][class_name] - np.mean(compute_metrics(new_ground_truth, new_predict)[0])
        # Both are negative because they should be maximized
    else:
        metric = - np.mean(compute_metrics(new_ground_truth, new_predict)[0])

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy", 
        metrics=[metric]
    )

    
    # Early stopping after 5 epochs 
    early_stopping = EarlyStopping(
    monitor='val_loss',  
    patience=5,  
    restore_best_weights=True,  
    verbose=1  
    )
    
    
    # including custom metrics in callbacks
    custom_metrics_callback = keras.callbacks.LambdaCallback(
    on_epoch_end=lambda epoch, logs: logs.update({
        "class_wise_iou": compute_metrics(new_ground_truth, new_predict)[0][class_name],
        "class_wise_dice_score": compute_metrics(new_ground_truth, new_predict)[1][class_name],
        "class_wise_accuracy": compute_metrics(new_ground_truth, new_predict)[2][class_name],
        "class_wise_precision": compute_metrics(new_ground_truth, new_predict)[3][class_name],
        "class_wise_recall": compute_metrics(new_ground_truth, new_predict)[4][class_name],
        "mean_iou": compute_metrics(new_ground_truth, new_predict)[5],
        "min_class_wise_iou": np.min(compute_metrics(new_ground_truth, new_predict)[0]),
        "max_class_wise_iou": np.max(compute_metrics(new_ground_truth, new_predict)[0]),
        "epoch": epoch,
        "loss": logs["loss"],
        "val_loss": logs["val_loss"]}))

    
    # callbacks and logging
    csv_logger = keras.callbacks.CSVLogger(
    input_directory + "logs/" + f"training_logs_{model_name}.csv",
    append=True
    )

    custom_metrics_csv_logger = CustomMetricsCSVLogger(
        input_directory + "logs/" + f"training_logs_{model_name}.csv",
        append=True
    )
    
    
    log_dir = "gs://tf_records_bucket/tf_records/Untitled Folder/logs/"  # Specify the directory to save logs
    tensorboard_callback = TensorBoard(log_dir=log_dir)

    output_of_image = "gs://tf_records_bucket/tf_records/Untitled Folder/output"
    from tensorflow.keras.models import load_model
    # Combine all callbacks
    all_callbacks = [
        keras.callbacks.ModelCheckpoint(model_path + model_name, save_best_only=False),
        tensorboard_callback,
        custom_metrics_callback,
        custom_metrics_csv_logger,  # Add the custom_metrics_csv_logger here
        # early_stopping,
        PredictSegmentationCallback(test_image_path, output_of_image)
    ]
    # Load the model if a checkpoint exists
    if os.path.exists(model_path + model_name):
        model = load_model(model_path + model_name)
        print("Loaded model from checkpoint")
    else:
        # If no checkpoint exists, create a new model
        model = get_model(
            img_size=img_size, num_classes=num_classes, num_bands=image_channels
        )
        model.compile(optimizer="adam", loss="categorical_crossentropy")
        print("Created a new model")

    # Continue training
    model_history = model.fit(
        train_dataset,
        epochs=num_epochs,
        callbacks=all_callbacks,
        batch_size=32,
        validation_data=val_dataset,
    )

    if early_stopping.stopped_epoch > 0:
        print(f"Training stopped at epoch {early_stopping.stopped_epoch} due to early stopping.")
    else:
        print("Training completed all epochs.")
    # Save the model after training
    # model.save(model_path + model_name)
    # print("Model saved locally")

    upload_blob(bucket_name, model_path + model_name, "model/" + model_name)
    print("Uploaded to cloud storage successfully")


    



if __name__ == "__main__":

    train()







# ! tensorboard --logdir gs://tf_records_bucket/tf_records/Untitled\ Folder/logs/ 



