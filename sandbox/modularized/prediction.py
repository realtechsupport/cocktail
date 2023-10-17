import keras
import numpy as np
import tensorflow as tf
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

model = keras.models.load_model('/home/otbuser/all/code/model.hdf5', compile=False)

num_classes = 23  # Total number of classes including class 0

# Define the class weights (0 for class 0, equal weight for other classes)
class_weights = np.ones(num_classes)
class_weights[0] = 0  # Set weight 0 for class 0
class_weights /= np.sum(class_weights)  # Normalize to ensure sum equals 1



def predict_segmentation(patches):
    # Make predictions using the loaded model

    seg_patches = []
    for patch in patches:
        image = tf.expand_dims(patch, axis=0)
        prediction = model.predict(image)
        weighted_prediction = np.argmax(prediction * class_weights, axis=-1)
        seg_patches.append(weighted_prediction)

    return seg_patches

# Load the GeoTIFF file
with rasterio.open('/home/otbuser/all/data/output.tif') as src:
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
patch_size = 256
patches = []
for i in range(0, cropped_array.shape[0], patch_size):
    for j in range(0, cropped_array.shape[1], patch_size):
        patch = cropped_array[i:i+patch_size, j:j+patch_size]
        patches.append(patch)
predicted_patches = predict_segmentation(patches)
stitched_array = np.zeros((3840,4608), dtype=cropped_array.dtype)
patch_idx = 0
for i in range(0, 3840, 256):
    for j in range(0, 4608, 256):
        patch = predicted_patches[patch_idx]
        stitched_array[i:i+256, j:j+256] = patch
        patch_idx += 1

# Create an array with class labels (example segmentation mask)
segmentation_mask = stitched_array  # Example labels



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

# Plot the segmentation mask using the custom colormap
image = ax.imshow(segmentation_mask, cmap=cmap, vmin=1, vmax=22)

# Add a colorbar to show the class-color mapping
cbar = plt.colorbar(image, ax=ax, ticks=list(class_colors.keys()))
cbar.set_label('Classes')

# Show the plot
plt.title('Segmentation Mask')
plt.savefig('/home/otbuser/all/data/'+'Segmentation-Mask-prediction.png')
plt.show()



