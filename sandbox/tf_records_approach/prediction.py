import os
import rasterio
from rasterio.mask import mask
import geopandas as gpd
from shapely.geometry import mapping
import tensorflow as tf
import keras
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import sys, os
from tensorflow import keras
import argparse
import random
import time

username = os.getenv("USER") or os.getenv("LOGNAME")

path = f"/home/{username}/project/trained_models/"


def parsing_user_info():
    parser = argparse.ArgumentParser(description="Select TIFF images from a directory.")
    parser.add_argument(
        "directory", help="Path to the directory containing TIFF images."
    )
    parser.add_argument(
        "choice", help="Enter 'all' to select all images, or enter a specific number."
    )
    parser.add_argument(
        "--output_directory", help="Directory to save the output.", default=None
    )
    args = parser.parse_args()

    try:
        selected_images = select_images(args.directory, args.choice)
    except ValueError as e:
        print(f"Error: {e}")

    image_paths = [
        os.path.join(args.directory, image_file) for image_file in selected_images
    ]
    return image_paths, args.output_directory


def select_images(image_directory, user_choice: str):
    # Use os.listdir to get all files in the directory
    all_files = os.listdir(image_directory)

    # Filter files with the ".tif" extension
    all_images = [file for file in all_files if file.endswith(".tif")]

    if user_choice.lower() == "all":
        # Option 1: Select all images
        selected_images = all_images

    elif user_choice.isdigit():
        # Option 2: Select a random number of images
        num_random_images = int(user_choice)

        if len(all_images) >= num_random_images:
            user_choice_manual = input(
                f"Do you want to manually select {num_random_images} images? (yes/no): "
            ).lower()

            if user_choice_manual == "yes":
                # Allow user to manually select images
                print("Available images:")
                for i, image in enumerate(all_images, start=1):
                    print(f"{i}. {image}")

                selected_indices = input(
                    "Enter the indices of the images you want to select (comma-separated): "
                )
                selected_indices = [
                    int(index.strip()) - 1
                    for index in selected_indices.split(",")
                    if index.strip().isdigit()
                ]

                selected_images = [
                    all_images[index]
                    for index in selected_indices
                    if 0 <= index < len(all_images)
                ]

                if len(selected_images) != num_random_images:
                    raise ValueError(
                        "Number of manually selected images does not match the specified count."
                    )

            else:
                # Randomly select images
                selected_images = random.sample(all_images, num_random_images)
        else:
            raise ValueError(
                "Selected random number of tiff files is greater than available tif files"
            )

    else:
        print("Invalid choice. Please enter 'all' or integer as string.")
        return

    # Print the selected images
    print("Selected Images:")
    for image_file in selected_images:
        print(os.path.join(image_directory, image_file))

    return selected_images


geojson_datapath = f"/home/{username}/project/labels/newextent_1123.geojson"


def clip_tiff(tiff, geojson=geojson_datapath):
    with open(geojson) as clip_geojson:
        clip_geojson = gpd.read_file(clip_geojson)
        clip_geometry = clip_geojson.geometry.values[0]
        clip_geojson = mapping(clip_geometry)
        # print(clip_geojson)

    # print("tiff",tiff)
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



def save_segmentation_mask(stitched_array, number, segmentation_dir=f"/home/{username}/project/docs"):
    class_colors = {
        1: (5, 5, 230),
        2: (190, 60, 15),
        3: (65, 240, 125),
        4: (105, 200, 95),
        5: (30, 115, 10),
        6: (255, 196, 34),
        7: (110, 85, 5),
        8: (235, 235, 220),
        9: (120, 216, 47),
        10: (84, 142, 128),
        11: (84, 142, 128),
        12: (84, 142, 128),
        13: (50, 255, 215),
        14: (50, 255, 215),
        15: (50, 255, 215),
        16: (193, 255, 0),
        17: (105, 200, 95),
        18: (105, 200, 95),
        19: (105, 200, 95),
        20: (193, 255, 0),
        21: (255, 50, 185),
        22: (255, 255, 255),
    }

    class_names = {
        1: "lake",
        2: "settlement",
        3: "shrub land",
        4: "grass land",
        5: "homogenous forest",
        6: "agriculture1 (with vegetation)",
        7: "agriculture2 (without vegetation)",
        8: "open area",
        9: "clove plantation",
        10: "mixed forest1",
        11: "mixed forest2",
        12: "mixed forest3",
        13: "rice field1",
        14: "rice field2",
        15: "rice field3",
        16: "mixed garden",
        17: "grass land2",
        18: "grass land3",
        19: "grass land4",
        20: "mixed garden2",
        21: "agroforestry",
        22: "clouds",
    }

    normalized_colors_array = np.array([tuple(np.array(v) / 255.0) for v in class_colors.values()])

    cmap = ListedColormap(normalized_colors_array)

    fig, ax = plt.subplots(figsize=(12, 8))

    image = ax.imshow(stitched_array, cmap=cmap, vmin=1, vmax=23)

    # Add class names to the colorbar
    cbar = plt.colorbar(image, ax=ax, ticks=list(class_colors.keys()))
    cbar.set_label("Classes")

    # Modify tick labels to include class names
    cbar.set_ticklabels([f"{i}. {class_names[i]}" for i in range(1, 23)])

    if segmentation_dir == f"/home/{username}/project/docs":
        plt.savefig(f"/home/{username}/project/docs/segmentation_mask.png")
        plt.close() 
    else:
        plt.savefig(segmentation_dir + f"segmentation_mask{number}.png")
        plt.close() 
    

def save_plain_image(image_array, number, save_path):
    class_colors = {
        1: (5, 5, 230),
        2: (190, 60, 15),
        3: (65, 240, 125),
        4: (105, 200, 95),
        5: (30, 115, 10),
        6: (255, 196, 34),
        7: (110, 85, 5),
        8: (235, 235, 220),
        9: (120, 216, 47),
        10: (84, 142, 128),
        11: (84, 142, 128),
        12: (84, 142, 128),
        13: (50, 255, 215),
        14: (50, 255, 215),
        15: (50, 255, 215),
        16: (193, 255, 0),
        17: (105, 200, 95),
        18: (105, 200, 95),
        19: (105, 200, 95),
        20: (193, 255, 0),
        21: (255, 50, 185),
        22: (255, 255, 255),
    }

    normalized_colors_array_for_plain_image = np.array([tuple(np.array(v) / 255.0) for v in class_colors.values()])

    cmap_plain = ListedColormap(normalized_colors_array_for_plain_image)
    # Set the figure size without white space
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot the image
    ax.imshow(image_array, cmap=cmap_plain)

    # Remove axes
    ax.set_axis_off()

    # Save the plain image without any additional information
    plt.savefig(save_path + f'plain_image{number}.png', bbox_inches='tight', pad_inches=0)
    plt.close() 


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


def prediction_function_img(test_image_path, number):
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
    print(f"Time taken for just for predictions: {elapsed_time} seconds")

    logits = predictions

    # Set values of class 0 to a very large negative number
    mask = tf.one_hot(
        0, depth=23, on_value=float("-inf"), off_value=0, dtype=tf.float32
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

    # start_time = time.time()
    save_segmentation_mask(stitched_array, number, output_directory)
    save_plain_image(stitched_array, number, output_directory)
    end_time = time.time()

    # Calculate the elapsed time
    elapsed_time_stitch = end_time - start_time

    # Print the elapsed time
    print(f"Time taken for prediction with stitching the mask: {elapsed_time_stitch} seconds")


if __name__ == "__main__":
    IMAGE_CHANNELS = 8  # 8 bands images as input

    model = keras.models.load_model(path + "patch_8_batch_32.hdf5")
    input_shape = model.layers[0].input_shape

    PATCH_HEIGHT = input_shape[0][-3]
    PATCH_WIDTH = input_shape[0][-2]

    test_image_paths, output_directory = parsing_user_info()

    for number, test_image_path in enumerate(test_image_paths):
        prediction_function_img(test_image_path, number)
