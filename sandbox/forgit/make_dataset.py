
#this module consists of functions that takes in raw dataset - 8 band image and corresponding mask
#and crops them, create patches, and sample useful patches that can be fed into the U-net model. 

# patch-size determines resizing the orignal image, how many patches can be made. 

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
                print(counts[0], (counts[0]/counts.sum())*100)
                if (1 - (counts[0]/counts.sum())) > 0.05:  #At least 5% useful area with labels that are not 0
                    Path(output_folder).mkdir(parents=True, exist_ok=True)
                    # Construct the output image file path
                    output_image_path = Path(output_folder) / Path(file_path).name
    
                    # Copy the input image to the output folder
                    shutil.copyfile(file_path, output_image_path)

                    print(f"Image copied to: {output_image_path}")
                else:
                    print("Condition not met: Image not copied.")



#--------Input images-----
datapath = '/Users/srikarreddy/geosegment/data/'
input_image_path = 'area2_0530_2022_8bands.tif'    
crop_size = 256
cropped_image = 'cropped_input.tif'
crop_to_nearest_patch_size(datapath, input_image_path, crop_size, cropped_image)

patch_path = '/Users/srikarreddy/geosegment/data/patches/'

patch_size = 256

extract_and_save_patches(datapath, patch_path, cropped_image, patch_size)

#-----Labels-------
label_image_path = 'OUTPUT.tif'    
cropped_label = 'cropped_label.tif'
crop_to_nearest_patch_size(datapath, label_image_path, crop_size, cropped_label)

label_path = '/Users/srikarreddy/geosegment/data/labels/'

extract_and_save_patches(datapath, label_path, cropped_label, patch_size)


#------sampling------

output_folder = '/Users/srikarreddy/geosegment/data/sampled_labels'

sampling(label_path,output_folder)

source_folder = '/Users/srikarreddy/geosegment/data/sampled_labels'
destination_folder = '/Users/srikarreddy/geosegment/data/patches'
new_folder = '/Users/srikarreddy/geosegment/data/sampled_patches'

# List files in the source folder
source_files = os.listdir(source_folder)

# Create the new folder if it doesn't exist
os.makedirs(new_folder, exist_ok=True)

# Loop through the files in the source folder
for filename in source_files:
    destination_file_path = os.path.join(destination_folder, filename)
    
    # Check if the file with the same name exists in the destination folder
    if os.path.exists(destination_file_path):
        shutil.copy(destination_file_path, new_folder)

print("Files copied successfully.")





