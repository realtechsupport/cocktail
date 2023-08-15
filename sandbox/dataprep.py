import os
import cv2
import numpy as np
import glob
import numpy as np
from matplotlib import pyplot as plt
from patchify import patchify
import tifffile as tiff
from PIL import Image
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.metrics import MeanIoU
import random
import rasterio 
from rasterio.windows import Window
from tensorflow.keras.utils import to_categorical
import shutil
from pathlib import Path


#-----------------------------------5a-----------------------------------------------------

def crop_to_nearest_patch_size(datapath, input_image_path, crop_size, croppedfilename):
    # Open the input image
    with rasterio.open(datapath + input_image_path) as src:
        # Get the width and height of the image
        width = src.width
        height = src.height

        # Calculate the new width and height that are multiples of the patch size
        new_width = int(np.ceil(width / crop_size)) * crop_size
        new_height = int(np.ceil(height / crop_size)) * crop_size

        # Calculate crop window
        left = (width - new_width) // 2
        top = (height - new_height) // 2
        right = left + new_width
        bottom = top + new_height
        window = Window(left, top, new_width, new_height)

        # Read the cropped data
        cropped_data = src.read(window=window)

        # Create a new cropped image
        profile = src.profile
        profile.update(width=new_width, height=new_height)

        # Save the cropped image
        with rasterio.open(datapath + croppedfilename, 'w', **profile) as dst:
            dst.write(cropped_data)

        print('5a. Cropping to nearest patch size completed!')

#-----------------------------------5b-----------------------------------------------------

def extract_and_save_patches(datapath, patch_path, cropped_image, patch_size):
    # Open the TIFF file
    with rasterio.open(datapath + cropped_image) as src:
        # Read the TIFF data
        tiff_data = src.read()

        # Get the shape of the TIFF data
        num_bands, height, width = tiff_data.shape

        # Calculate the number of patches in each dimension
        num_patches_height = height // patch_size[0]
        num_patches_width = width // patch_size[1]

        # Extract and save multiband patch images
        patch_id = 0
        for i in range(num_patches_height):
            for j in range(num_patches_width):
                # Calculate the patch boundaries
                h_start = i * patch_size[0]
                h_end = (i + 1) * patch_size[0]
                w_start = j * patch_size[1]
                w_end = (j + 1) * patch_size[1]

                # Extract the multiband patch
                patch = tiff_data[:, h_start:h_end, w_start:w_end]

                # Create a new TIFF file for the patch
                patch_file = patch_path + f'patch_{patch_id}.tif'
                with rasterio.open(patch_file, 'w', driver='GTiff', height=patch_size[0], width=patch_size[1],
                                   count=num_bands, dtype=patch.dtype) as dst:
                    for band in range(num_bands):
                        dst.write(patch[band], band + 1)

                patch_id += 1

    print('5b. Patch extraction and saving completed!')

#-----------------------------------5c-----------------------------------------------------

def read_tiff_files_from_folder(patch_path):
    # Initialize an empty list to store the arrays
    arrays_list = []

    # Iterate through the TIFF files in the folder
    for filename in os.listdir(patch_path):
        if filename.endswith(".tif"):
            file_path = os.path.join(patch_path, filename)

            # Open the TIFF file
            with rasterio.open(file_path) as src:
                # Read all bands of the TIFF file as a NumPy array
                array = src.read()

                # Add the array to the list
                arrays_list.append(array)
    
    print('5c. Reading tif files and generating arrays list completed!')
    return arrays_list

#-----------------------------------5d-----------------------------------------------------

def normalize_images(images):
    # Normalize each band of the image
    normalized_images = np.zeros_like(images, dtype='float32')
    for band in range(images.shape[1]):
        band_min = np.min(images[:, band])
        band_max = np.max(images[:, band])
        normalized_images[:, band] = (images[:, band] - band_min) / (band_max - band_min)
    
    print('5d. Normilization completed!')
    return normalized_images

#-----------------------------------5e-----------------------------------------------------

def reshape_images(normalized_images, p_size1, p_size2, num_bands):
    # Reshape the normalized images
    reshaped_images = normalized_images.reshape(-1, p_size1, p_size2, num_bands)

    print('5e. Reshaping normalized images completed!')
    return reshaped_images 

def sampling(patch_path,output_folder):
       # Iterate through the TIFF files in the folder
    
    for filename in os.listdir(patch_path):
        if filename.endswith(".tif"):
            file_path = os.path.join(patch_path, filename)

            # Open the TIFF file
            with rasterio.open(file_path) as src:
                # Read all bands of the TIFF file as a NumPy array
                array = src.read()

                val, counts = np.unique(array, return_counts=True)
    
                if (1 - (counts[0]/counts.sum())) > 0.05:  #At least 5% useful area with labels that are not 0
                    Path(output_folder).mkdir(parents=True, exist_ok=True)
                    # Construct the output image file path
                    output_image_path = Path(output_folder) / Path(file_path).name
    
                    # Copy the input image to the output folder
                    shutil.copyfile(file_path, output_image_path)

                    print(f"Image copied to: {output_image_path}")
                else:
                    print("Condition not met: Image not copied.")



    

#-----------------------------------Main---------------------------------------------------
# def main():
#     datapath = '/home/otbuser/all/data/'
#     input_image_path = 'area2_0530_2022_8bands.tif'
#     crop_size = 256

#     crop_to_nearest_patch_size(datapath, input_image_path, crop_size)

#     patch_path = '/home/otbuser/all/data/patches/'
#     cropped_image = 'cropped_input.tif'
#     patch_size = (256, 256)

#     extract_and_save_patches(datapath, patch_path, cropped_image, patch_size)

#     arrays_list = read_tiff_files_from_folder(patch_path)

#     images = np.array(arrays_list)

#     normalized_images = normalize_images(images)

#     p_size1 = 256
#     p_size2 = 256
#     num_bands = 8
#     reshaped_images = reshape_images(normalized_images, p_size1, p_size2, num_bands)

# if __name__ == "__main__":
#     main()

# 5a
# def cropTiff(inputFile, outputDir=None):

#     with rasterio.open(inputFile) as file:
#         height = file.height
#         width = file.width
        
#         # Calculate the smallest multiple of 256 that is greater than or equal to the width and height of the image
#         crop_width = int(np.ceil(width / 256.0)) * 256
#         crop_height = int(np.ceil(height / 256.0)) * 256

#         # Calculate crop window
#         left = (width - crop_width) // 2
#         top = (height - crop_height) // 2
#         right = left + crop_width
#         bottom = top + crop_height
#         window = Window(left, top, crop_width, crop_height)

#         # Read the cropped data
#         cropped_data = file.read(window=window)

#         # Create a new cropped TIFF file
#         profile = file.profile
#         profile.update(width=crop_width, height=crop_height)

#         with rasterio.open(outputDir+'cropped_input.tif', 'w', **profile) as dst:
#             dst.write(cropped_data)
# 5f
def onehotencoding(labels, num_classes=23):
    return to_categorical(labels, num_classes)

