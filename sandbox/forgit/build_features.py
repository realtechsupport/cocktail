
#this module has functions that help create features from the data that can be fed into
#neural net - normalizing input patches, reshaping, one-hotencoding labels.
import rasterio
import os
import numpy as np
from tensorflow.keras.utils import to_categorical

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
    
    print('Reading tif files and generating arrays list completed!')
    return arrays_list



def normalize_images(images):
    # Normalize each band of the image
    normalized_images = np.zeros_like(images, dtype='float32')
    for band in range(images.shape[1]):
        band_min = np.min(images[:, band])
        band_max = np.max(images[:, band])
        normalized_images[:, band] = (images[:, band] - band_min) / (band_max - band_min)
    
    print('Normilization completed!')
    return normalized_images

#----------------------------------------------------------------------------------------

def reshape_images(normalized_images, patch_size, num_bands):
    # Reshape the normalized images
    reshaped_images = normalized_images.reshape(-1, patch_size, patch_size, num_bands)

    print('Reshaping normalized images completed!')
    return reshaped_images

#---------------------------------------------------------------------------------------


def onehotencoding(labels, num_classes=23):
    return to_categorical(labels, num_classes)
