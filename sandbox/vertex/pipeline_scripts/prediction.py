import rasterio
from rasterio.mask import mask
import geopandas as gpd
from shapely.geometry import mapping
import tensorflow as tf
import time
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns
import fsspec
import json

# """1. reshape the input image to the size of label
# 2. create boolean mask
# boolean_mask = label_array != 0
# 3. apply boolean mask to resized prediction
# new_predict = np.where(boolean_mask,resized_prediction_array,0)
# 4. send the label_array and new_predict into the compute_metrics
# """

class_names = [
    "lake",
    "settlement",
    "shrub land",
    "grass land",
    "homogenous forest",
    "agriculture1 (with vegetation)",
    "agriculture2 (without vegetation)",
    "open area",
    "clove plantation",
    "mixed forest1",
    "mixed forest2",
    "rice field1",
    "rice field2",
    "rice field3",
    "mixed garden",
    "grass land2",
    "grass land3",
    "mixed garden2",
    "agroforestry",
    "clouds",
]



def load_config(file_path):
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config




config = load_config('./pipeline_scripts/config.json')

geojson_datapath = 'gs://tf_records_bucket/labels/new_extent_1123.geojson'


num_classes = config.get("num_classes")
model_path = config.get("model_path")
# model_path = "eval_and_pred/trained_model/patch_h8_w8_batch_32_on_0530_2022.hdf5"
IMAGE_CHANNELS = config.get("num_bands")  # 8 bands images as input

model = keras.models.load_model(model_path)
input_shape = model.layers[0].input_shape

PATCH_HEIGHT = input_shape[0][-3]
PATCH_WIDTH = input_shape[0][-2]



def clip_tiff(tiff, geojson = geojson_datapath):
    # Read the GeoJSON content using fsspec and geopandas
    with fsspec.open(geojson, 'r') as f:
        clip_geojson = gpd.read_file(f)
        clip_geometry = clip_geojson.geometry.values[0]
        clip_geojson = mapping(clip_geometry)

    # Open the TIFF file using rasterio
    print("prediction.clip_tiff, tiff", tiff)
    with rasterio.Env():
        with rasterio.open(tiff) as src:
            # Perform the clip
            clip_image, clip_transform = mask(src, [clip_geojson], crop=True)

    return clip_image

def tensorify_image(image):
    ## resizing and process input funciton condensed into one.
    tensor_image = tf.convert_to_tensor(image)
    tensor_image = tf.transpose(tensor_image, perm=[1, 2, 0])
    return tensor_image


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
    print(image.shape)
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


def tile_image(fullimg, CHANNELS=1, TILE_HT=128, TILE_WD=128):
    print(fullimg.shape)
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
    all_tiles = tf.reshape(tiles, [nrows * ncols, TILE_HT, TILE_WD, CHANNELS])
    ordered_tiles = tf.reshape(tiles, [nrows, ncols, TILE_HT, TILE_WD, CHANNELS])
    return ordered_tiles, all_tiles, fullimg.shape



def stitch_segmentation_patches(segmentation_patches, dims, PATCH_HEIGHT, PATCH_WIDTH):
    height, width = dims[0], dims[1]
    num_rows, num_cols = segmentation_patches.shape[:2]

    # Convert TensorFlow tensor to NumPy array
    segmentation_patches_np = segmentation_patches.numpy()

    stitched_array = np.zeros((height, width), dtype=int)

    # Reshape the segmentation_patches array
    segmentation_patches_reshaped = segmentation_patches_np.reshape(
        (num_rows, num_cols, PATCH_HEIGHT, PATCH_WIDTH)
    )
    print("segmentation_patches_reshaped.shape", segmentation_patches_reshaped.shape)

    # Calculate the indices for stitching
    row_indices_patch = np.arange(0, height, PATCH_HEIGHT)
    col_indices_patch = np.arange(0, width, PATCH_WIDTH)
    print("row_indices_patch", row_indices_patch.shape)
    print("col_indices_patch", col_indices_patch.shape)

    # Use nested loops to stitch patches into the final array
    for i in range(num_rows):
        for j in range(num_cols):
            row_start = row_indices_patch[i]
            col_start = col_indices_patch[j]
            row_end = row_start + PATCH_HEIGHT
            col_end = col_start + PATCH_WIDTH

            stitched_array[
                row_start:row_end, col_start:col_end
            ] = segmentation_patches_reshaped[i, j]

    print("stitched_array", stitched_array.shape)
    return stitched_array


def prediction_function_img(test_image_path):
    image = clip_tiff(test_image_path)
    new_image = tensorify_image(image)
    normalized_image = bandwise_normalize(new_image)
    display_patches, inference_patches, dims = tile_image(
        normalized_image, IMAGE_CHANNELS, PATCH_HEIGHT, PATCH_WIDTH
    )
    print("dims", dims)
    start_time = time.time()
    predictions = model.predict(inference_patches, batch_size=2048)
    end_time_pred = time.time()

    # Calculate the elapsed time
    elapsed_time = end_time_pred - start_time

    # Print the elapsed time
    print(f"Time taken for predictions: {elapsed_time} seconds")

    logits = predictions

    # Set values of class 0 to a very large negative number
    mask = tf.one_hot(
        0, depth=num_classes, on_value=float("-inf"), off_value=0, dtype=tf.float32
    )
    logits_with_mask = logits + mask

    # Perform argmax along the last axis (axis=-1)
    argmax_result = tf.argmax(logits_with_mask, axis=-1)

    tiles = display_patches
    nrows = tiles.shape[0]
    ncols = tiles.shape[1]
    segmentation_patches = tf.reshape(
        argmax_result, [nrows, ncols, PATCH_HEIGHT, PATCH_WIDTH]
    )

    stitched_array = stitch_segmentation_patches(
        segmentation_patches, dims, PATCH_HEIGHT, PATCH_WIDTH
    )

    end_time = time.time()

    # Calculate the elapsed time
    elapsed_time_stitch = end_time - start_time

    # Print the elapsed time
    print(f"Time taken including stitching: {elapsed_time_stitch} seconds")

    return stitched_array


