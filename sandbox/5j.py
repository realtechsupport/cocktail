import rasterio
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from keras.models import load_model

def predict_segmentation_mask(data_file, model_file, patch_size=256, n_classes=23):
    # Read the TIFF file and convert to NumPy array
    with rasterio.open(data_file) as src:
        new_array = src.read()
    img = np.array(new_array)

    # Normalize each band of the image
    large_img = np.zeros_like(img, dtype='float32')
    for band in range(img.shape[1]):
        band_min = np.min(img[:, band])
        band_max = np.max(img[:, band])
        large_img[:, band] = (img[:, band] - band_min) / (band_max - band_min)

    reshaped_image = large_img.reshape(-1, patch_size, patch_size, img.shape[1])

    # Load the pre-trained model
    model = load_model(model_file, compile=False)

    # Make predictions using the model
    output = model.predict(reshaped_image)

    # Reshape the output array and take argmax to get the predicted class indices
    segmentation_masks = output[0]
    predicted_classes = np.argmax(segmentation_masks, axis=-1)

    # Create a colormap for visualizing different classes
    cmap = plt.get_cmap('tab20', segmentation_masks.shape[-1])

    # Visualize the segmentation mask
    plt.imshow(predicted_classes, cmap=cmap)
    plt.colorbar()
    plt.title('Segmentation Mask')
    plt.show()

    # Save the segmentation mask as an image
    output_image = Image.fromarray(np.uint8(predicted_classes))
    output_image.save('segmentation_mask.png')

# Need to Edit this once
data_file_path = '/home/otbuser/all/data/patches/'
model_file_path = '/home/otbuser/all/data/patches/landcover_model.hdf5'
predict_segmentation_mask(data_file_path, model_file_path)
