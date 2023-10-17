import numpy as np
import rasterio
import keras
import tensorflow as tf
from tensorflow.keras.utils import to_categorical



def onehotencoding(labels, num_classes=23):
    return to_categorical(labels, num_classes)


# This function preprocess the geoimage file, normalizes and crops.
def preprocess_images(datapath, file_name):
    with rasterio.open(datapath+file_name) as src:
        # Read the TIFF data
        tiff_data = src.read()

        # Get the shape of the TIFF data
        num_bands, height, width = tiff_data.shape

        print("Original image dimensions:", num_bands, height, width)

        print(np.min(tiff_data), np.max(tiff_data))


        normalized_image = np.zeros_like(tiff_data, dtype='float32')

        for band, count in enumerate(range(tiff_data.shape[0])):
            band_data = tiff_data[band, :, :]
            band_min = np.min(band_data)
            band_max = np.max(band_data)
            print("band-", count+1,"maximum-",band_max,"minimum-",band_min)
            #print(band_data)
            normalized_band = (band_data - band_min) / (band_max - band_min + 1e-10)
            normalized_image[band, :, :] = normalized_band


        # Calculate the new width and height that are multiples of the patch size
        patch_size = 256  # Replace with your desired patch size
        new_width = int(np.floor(width / patch_size)) * patch_size
        new_height = int(np.floor(height / patch_size)) * patch_size

        print("cropped dimensions:", new_height, new_width)

        input_image = np.moveaxis(normalized_image, 0, -1)

        # Crop the input_image to the new dimensions
        cropped_array = input_image[:new_height, :new_width, :]

    print("Cropped array shape:", cropped_array.shape)
    print(np.min(cropped_array), np.max(cropped_array))
    patches = []
    for i in range(0, cropped_array.shape[0], patch_size):
        for j in range(0, cropped_array.shape[1], patch_size):
            patch = cropped_array[i:i+patch_size, j:j+patch_size]
            patches.append(patch)
    
    training_images = np.array(patches)
    return training_images, height, width

def preprocess_masks(datapath, file_name, height, width):
    with rasterio.open(datapath+file_name) as src:
        # Read the TIFF data
        output_mask = src.read()

        # Calculate the new width and height that are multiples of the patch size
        patch_size = 256  # Replace with your desired patch size
        new_width = int(np.floor(width / patch_size)) * patch_size
        new_height = int(np.floor(height / patch_size)) * patch_size

        print("cropped dimensions:", new_height, new_width)

        output_mask = np.moveaxis(output_mask, 0, -1)

        # Crop the input_image to the new dimensions
        cropped_mask = output_mask[:new_height, :new_width, :]
    
    print("Cropped array shape:", cropped_mask.shape)
    new_mask = np.squeeze(cropped_mask)
    masks = []
    for i in range(0, new_mask.shape[0], patch_size):
        for j in range(0, new_mask.shape[1], patch_size):
            patch = new_mask[i:i+patch_size, j:j+patch_size]
            masks.append(patch)
    mask_array = np.array(masks)
    return mask_array

    
def sampling(training_images, mask_array):
    useful_images = []
    useful_masks = []
    useless = 0
    indexes = []
    for img in range(len(training_images)):
        img_name=training_images[img]
        mask_name = mask_array[img]

        val, counts = np.unique(mask_name, return_counts=True)

        if (1 - (counts[0]/counts.sum())) > 0.05:
            useful_images.append(img_name)
            useful_masks.append(mask_name)
            indexes.append(img)
            print("I am useful")

        else:
            print("I am useless")
            useless +=1

    print("Total useful images are: ", len(training_images)-useless)
    print("Total useless images are: ", useless)
    
    useful_training_images = np.array(useful_images)
    useful_training_masks_array = np.array(useful_masks)

    useful_training_masks = onehotencoding(useful_training_masks_array)

    return useful_training_images, useful_training_masks
