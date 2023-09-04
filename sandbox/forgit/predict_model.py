# 1. get the model and load it
# 2. apply preprocessing: resize, normalize, patchify and make it iterably available to predict function
# 4. Stitch the predicted output together
# 5. Visualize
# 6. overlay

import keras
import rasterio
import numpy as np
from rasterio.windows import Window
from data_processing import *
from build_features import *

#1 get the model and load 

model = keras.models.load_model('/Users/srikarreddy/geosegment/models/work_model.hdf5')

#2 get the large image and apply preprocessing steps

#2.1 cropping
datapath = '/Users/srikarreddy/geosegment/data/inference/'
input_image_path = 'area2_0530_2022_8bands.tif'    
crop_size = 256
cropped_image = 'cropped_input.tif'
crop_to_nearest_patch_size(datapath, input_image_path, crop_size, cropped_image)

with rasterio.open(datapath + cropped_image) as src:
        # Read the TIFF data
        tiff_data = src.read()

        # Get the shape of the TIFF data
        num_bands, height_cropped, width_cropped = tiff_data.shape

#2.2 create patches:

patch_path = '/Users/srikarreddy/geosegment/data/inference/patches/'
patch_size = 256
extract_and_save_patches(datapath, patch_path, cropped_image, patch_size)

#2.3 normalize and reshape 
arrays_list = read_tiff_files_from_folder(patch_path)
images = np.array(arrays_list)
normalized_images = normalize_images(images)
patch_size = 256
num_bands = 8
reshaped_images = reshape_images(normalized_images, patch_size, num_bands)

print(reshaped_images.shape)

num_images, height, width, num_bands = reshaped_images.shape
num_classes = 23

results = []
for i in range(num_images):
    input_image = reshaped_images[i]
    predicted_mask = model.predict(np.expand_dims(input_image, axis=0))  # Add batch dimension
    predicted_mask = np.argmax(predicted_mask, axis=-1)  # Perform argmax processing

    results.append(predicted_mask)

# Stack the results back into an array
results_array = np.stack(results, axis=0)
results_array = np.squeeze(results_array, axis=1) 

print("Results array shape:", results_array.shape)

# Assuming your array is named 'data'
unique_values, unique_counts = np.unique(results_array, return_counts=True)

# Print the unique values and their counts
for value, count in zip(unique_values, unique_counts):
    print(f"Value: {value}, Count: {count}")

#--------------eval-------------------

#------------------

# Assuming your stitched array has shape (304, 256, 256)
stitched_array = results_array  # Your numpy array

# Desired dimensions of the final stitched image
desired_height = height_cropped
desired_width = width_cropped

# Calculate the number of rows and columns needed for tiling
num_rows = desired_height // stitched_array.shape[1]
num_cols = desired_width // stitched_array.shape[2]

from PIL import Image

# Create an empty image with desired dimensions
output_image = Image.new('RGB', (desired_width, desired_height), (0, 0, 0))  # 'RGB', black background

# Define a colormap for color-coding classes (adjust as needed)
class_colors = {
    0: (0,0,0), #background
    1: (5, 5, 230),    # lake
    2: (190, 60, 15),  # settlement
    3: (65, 240, 125), # shrub land
    4: (105, 200, 95), # grass land
    5: (30, 115, 10),  # homogenous forest
    6: (255, 196, 34), # agriculture1
    7: (110, 85, 5),   # agriculture2
    8: (235, 235, 220),# open area
    9: (120, 216, 47), # clove plantation
    10: (84, 142, 128),# mixed forest1
    11: (84, 142, 128),# mixed forest2
    12: (84, 142, 128),# mixed forest3
    13: (50, 255, 215),# rice field1
    14: (50, 255, 215),# rice field2
    15: (50, 255, 215),# rice field3
    16: (193, 255, 0), # mixed garden
    17: (105, 200, 95),# grass land2
    18: (105, 200, 95),# grass land3
    19: (105, 200, 95),# grass land4
    20: (193, 255, 0), # mixed garden2
    21: (255, 50, 185),# agroforestry
    22: (255, 255, 255),# cloud
}

# Paste class values with color-coding
for row_idx in range(num_rows):
    for col_idx in range(num_cols):
        idx = row_idx * num_cols + col_idx
        if idx < stitched_array.shape[0]:
            class_values_row = stitched_array[idx]  # Get the row of class values
            colored_pixels = []
            for class_label_array in class_values_row:
                int_class_label = int(class_label_array[0])  # Convert to integer
                color = class_colors[int_class_label]
                colored_pixels.extend([color] * stitched_array.shape[2])
            colored_image = Image.new('RGB', (stitched_array.shape[2], stitched_array.shape[1]))
            colored_image.putdata(colored_pixels)
            output_image.paste(colored_image, (col_idx * stitched_array.shape[2], row_idx * stitched_array.shape[1]))

# Resize the image to the desired dimensions (if needed)
output_image = output_image.resize((desired_width, desired_height), Image.NEAREST)  # Change interpolation method if needed


# Save the final color-coded image
output_image.save("/Users/srikarreddy/geosegment/data/inference/0109_color_coded_image.png")  # You can change the format as needed

