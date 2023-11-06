import keras
import numpy as np
import tensorflow as tf
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datapreprocessing import *
import sys, os
from google.cloud import storage


def predict_segmentation(patches):
    # Make predictions using the loaded model

    seg_patches = []
    for patch in patches:
        image = tf.expand_dims(patch, axis=0)
        prediction = model.predict(image)
        weighted_prediction = np.argmax(prediction * class_weights, axis=-1)
        seg_patches.append(weighted_prediction)

    return seg_patches

def prediction_visual(segmentation_masks_arrays):

    # Define the class-color mapping
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
    cmap = ListedColormap(colors)

    # Create a figure and axis for the plot
    fig, ax = plt.subplots(figsize=(10, 8))

    for index,segmentation_mask in enumerate(segmentation_masks_arrays):

      # Plot the segmentation mask using the custom colormap
      image = ax.imshow(segmentation_mask, cmap=cmap, vmin=1, vmax=20)

      # Add a colorbar to show the class-color mapping
      cbar = plt.colorbar(image, ax=ax, ticks=list(class_colors.keys()))
      cbar.set_label('Classes')

      # Show the plot
      plt.title(f'Segmentation Mask_{index}')
      plt.savefig('/home/otbuser/all/data/'+f'Segmentation-Mask-prediction_{index}.png')
      #plt.show()

def predict_images_in_folder(datapath, patch_size, roipath,roishape = 'area2_square.geojson'):

    segmentation_masks_arrays= []

    # Loop through all files in the folder
    for ps in os.listdir(datapath):

        # Apply clipping
        clipped_image_path = newclipping(datapath,roipath,ps, roishape)

        # Preprocess(normalize,resize,create patches) the clipped image
        patches, CA = preprocessing(clipped_image_path, patch_size)
        #print(len(patches))

        #get predictions for each patch
        predicted_patches = predict_segmentation(patches)

        height = CA.shape[0]
        width = CA.shape[1]

        stitched_array = np.zeros((height,width), dtype=CA.dtype)
        patch_idx = 0
        for i in range(0, height, patch_size):
            for j in range(0, width, patch_size):
                patch = predicted_patches[patch_idx]
                stitched_array[i:i+patch_size, j:j+patch_size] = patch
                patch_idx += 1

        segmentation_masks_arrays.append(stitched_array)
    prediction_visual(segmentation_masks_arrays)


datapath = '/home/otbuser/all/data/images/'
roipath = '/home/otbuser/all/data/roi_folder/'
patch_size = 16
model_path = '/home/otbuser/all/code/multi_image_model.hdf5'

model = keras.models.load_model(model_path, compile=False)

num_classes = 23  # Total number of classes including class 0

# Define the class weights (0 for class 0, equal weight for other classes)
class_weights = np.ones(num_classes)
class_weights[0] = 0  # Set weight 0 for class 0
class_weights /= np.sum(class_weights)  # Normalize to ensure sum equals 1

# call predict_images_in_folder()
predict_images_in_folder(datapath, patch_size, roipath)
