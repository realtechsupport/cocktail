
import os
import numpy as np
import rasterio 
from rasterio.windows import Window
import shutil
from pathlib import Path



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

        print('Cropping to nearest patch size completed!')

def extract_and_save_patches(datapath, patch_path, cropped_image, patch_size):
    # Open the TIFF file
    with rasterio.open(datapath + cropped_image) as src:
        # Read the TIFF data
        tiff_data = src.read()

        # Get the shape of the TIFF data
        num_bands, height, width = tiff_data.shape

        # Calculate the number of patches in each dimension
        num_patches_height = height // patch_size
        num_patches_width = width // patch_size

        # Extract and save multiband patch images
        patch_id = 0
        for i in range(num_patches_height):
            for j in range(num_patches_width):
                # Calculate the patch boundaries
                h_start = i * patch_size
                h_end = (i + 1) * patch_size
                w_start = j * patch_size
                w_end = (j + 1) * patch_size

                # Extract the multiband patch
                patch = tiff_data[:, h_start:h_end, w_start:w_end]

                # Create a new TIFF file for the patch
                patch_file = patch_path + f'patch_{patch_id}.tif'
                with rasterio.open(patch_file, 'w', driver='GTiff', height=patch_size, width=patch_size,
                                   count=num_bands, dtype=patch.dtype) as dst:
                    for band in range(num_bands):
                        dst.write(patch[band], band + 1)

                patch_id += 1

    print('Patch extraction and saving completed!')