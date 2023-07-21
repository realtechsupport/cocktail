### Creating U-net compatabile patch-labels from .gpkg file, and training custom U-net, instead of relying on [OTBTF](https://otbtf.readthedocs.io/en/latest/api_tutorial.html). 

#### We are creating a custom u-net and a data pipeline suited for our situation. Refer to [Digitalsreeni youtube channel's playlist on U-net](https://www.youtube.com/playlist?list=PLZsOBAyNTZwbR08R959iCvYT3qzhxvGOE) - particularly videos [228](https://www.youtube.com/watch?v=jvZm8REF2KY&list=PLZsOBAyNTZwbR08R959iCvYT3qzhxvGOE&index=29) and [230](https://www.youtube.com/watch?v=0W6MKZqSke8&list=PLZsOBAyNTZwbR08R959iCvYT3qzhxvGOE&index=31) and the corresponding code in his [github](https://github.com/bnsreenu/python_for_microscopists/tree/master/230_landcover_dataset_segmentation) to understand everything you need to know about U-nets and geo-spatial segmentation. While the data processing, U-net modelling, and training framework is inspired from him, we are using Rasterio instead of cv2, patchify, etc. during the pre-processing steps. 

#### follow the below steps until step 4 to create your mask file. From step 5, although I have included code from my notebook, we need to create proper functions and a script to do those tasks. Refer to the [colab notebook](https://github.com/realtechsupport/cocktail/blob/main/sandbox/landcover.ipynb) if needed. 

## 1. Understand our data: 
We have our input image (8 band tif file) but we don't have a mask/labelled image which corresponds to that input. The label information is currently stored in .gpkg file. We can open that file in qgis and align it with our input 8-band image and visually see that polygons on .gpkg file corresponds to different terrain-classes. These polygons belongs to different classes of terrain. These polygons belong to 22 such classes, we could color these polygons into different colors based on their class, to see how they represent different terrain classes. To color the polygons based on the class, select the .gpkg file, go to properties, go to symbology, select categorized, select value - class, select random colors option in color ramp, and click classify.

![gpkg with colors](https://github.com/realtechsupport/cocktail/blob/main/sandbox/images/1.png "gpkg")
![gpkg with map](https://github.com/realtechsupport/cocktail/blob/main/sandbox/images/1.1.png "gpkg")


## 2.
There's a way in qgis to convert this .gpkg file into a mask/label tif file which only contains the information as to which class does each pixel belongs to. This mask/label file should exactly correspond to the input 8 band tif file. Each pixel value in mask/label file should give us information as to which class the corresponding pixel value in the input 8-band tif file belongs to. So, we need to generate a mask tif file that should have the exact same size of the input 8 band tif file and should also contain class-label information embedded into pixels based on .gpkg file. 

>a. select the .gpkg file and go to raster, and select conversion, and then vector to raster
![convert to raster](https://github.com/realtechsupport/cocktail/blob/main/sandbox/images/2.a.png "raster")
>b. In the pop up window, make sure the input layer is just .gpkg file
![window](https://github.com/realtechsupport/cocktail/blob/main/sandbox/images/2.b.png "select")
>c. In the "field to "use for a burn-in value" select the option - class
>d. select the output rasterize units to pixels
>e. change the width to (4618) and height to 4019. These the width and height of the input image. 
![width and height](https://github.com/realtechsupport/cocktail/blob/main/sandbox/images/2.e.png "w&h")
>f. In the output extent, click on the down-arrow beside the map, click on calculate from layer, and select the input 8-band file. 
>g. In the "rasterized", select save to a temporary file. Make sure the "open the file after running the algorithm" is checked
>h. hit run. A file name rasterized should open in qgis. Click on the properties and click on its path to see where it is stored. It gets stored in some oscure location. Save it whereever you feel is accessible. 

(If any error or remarks in red are seen, it is probably because you have forgotten one of the above steps/misconfigured a few settings.)

FYI: Behind-the-scenes qgis is running this code: (you can get this from advanced options in the window)
```
GDAL command:
gdal_rasterize -l area2_0123_2023_raster_classification_13 -a class -ts 4618.0 4019.0 -a_nodata 0.0 -te 281019.0 9079545.0 294873.0 9091602.0 -ot Float32 -of GTiff /Users/srikarreddy/Downloads/area2_0123_2023_raster_classification_13.gpkg /private/var/folders/yg/wlth31tn0_b1kwhrb_l4mw_c0000gn/T/processing_lEiEJW/14d9088e04f24432ab80b2a130fb0f36/OUTPUT.tif
```
In future, one could automate this mask creation process for a batch of images using a script without manually creating mask for each input image based on .gpkg file using qgis. But, It would be a bit much to do it programmatically for just one image or a hand-ful of images though. I feel doing it with qgis is clear and simple. 

## 3. 
We have now succesfully created the mask file which of same dimension as that of input file. The pixels in this file have the information as to which class the corresponding pixels in the input file belongs to. You can see that min value of the pixel is 1, max is 22, and no-data(background) value is 0. So, we bascially have 23 classes (22 labelled classes and 1 background dummy class) which correspond to our input file. 

![rasterized](https://github.com/realtechsupport/cocktail/blob/main/sandbox/images/3.a.png "rasterized")
![properties](https://github.com/realtechsupport/cocktail/blob/main/sandbox/images/3.b.png "info")

## 4. 
It's time to check programmatically if we generated a mask file that is of proper dimensions and contain the desired values or not. Rasterio is a python geospatial library which does the job. (Rasterio was primarily built because people wanted a geo-spatial library that is truly pythonic and intuitive. I ♡ Rasterio. Its documentation is very good. We are gonna use Rasterio for pretty much everything. We are using it for creating patches, converting tif files to numpy arrays, and repackaging numpy arrays to tif, and imaging tif files, etc.)

```
pip install rasterio
import rasterio
src = rasterio.open('OUTPUT.tif')
src.profile

{'driver': 'GTiff', 'dtype': 'float32', 'nodata': 0.0, 'width': 4618, 'height': 4019, 'count': 1, 'crs': CRS.from_epsg(32750), 'transform': Affine(3.0, 0.0, 281019.0,
       0.0, -3.0, 9091602.0), 'blockysize': 1, 'tiled': False, 'interleave': 'band'}
````

Check if you're able to get a similar output profile as above. The width and height should be same as the input file and the dtype should be a float32. 

## 5.
From here on, we need to build a single script that needs following functions and actions: 

a. A function that crops the input and mask files to the nearest size that is divisible by the desired patch size. This function should be used to crop the file into a size that is divisible by the desired patch size.

```
import rasterio
import numpy as np

# Open the tif image
with rasterio.open("image.tif") as src:

  # Get the width and height of the image
  width = src.width
  height = src.height

  # Calculate the smallest multiple of 256 that is greater than or equal to the width and height of the image
  new_width = int(np.ceil(width / 256.0)) * 256
  new_height = int(np.ceil(height / 256.0)) * 256

print(new_width,new_height)
```
```
import rasterio
from rasterio.windows import Window

# Define crop dimensions
crop_width = 4864
crop_height = 4096

# Open the TIFF file
with rasterio.open('image.tif') as src:
    # Calculate crop window
    left = (src.width - crop_width) // 2
    top = (src.height - crop_height) // 2
    right = left + crop_width
    bottom = top + crop_height
    window = Window(left, top, crop_width, crop_height)

    # Read the cropped data
    cropped_data = src.read(window=window)

    # Create a new cropped TIFF file
    profile = src.profile
    profile.update(width=crop_width, height=crop_height)

    with rasterio.open('output.tif', 'w', **profile) as dst:
        dst.write(cropped_data)
```

b. A function to chop up a given tif file into patches of the given patch size and save it in a folder in a orderly manner. This function should be used for chopping up the input and mask file into image-patches and their corresponding label-patches of desired patch size.

```
import rasterio
import numpy as np

# Open the TIFF file
with rasterio.open('output.tif') as src:
    # Define patch dimensions
    patch_size = (256, 256)

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
            patch_file = f'patch_{patch_id}.tif'
            with rasterio.open(patch_file, 'w', driver='GTiff', height=patch_size[0], width=patch_size[1],
                               count=num_bands, dtype=patch.dtype) as dst:
                for band in range(num_bands):
                    dst.write(patch[band], band + 1)

            patch_id += 1
```

c. A function that takes in the input patch-images or label-patches and converts them into numpy-arrays and group them together into a single numpy array (no_of_images, channels, patch-size, patch-size). As the label-patch has only one channel, it output dimension would (no_of_images,patch-size,patch-size).

```
import rasterio
import numpy as np
import os

# Set the folder path
folder_path = '/content/data/train_images/train'

# Initialize an empty list to store the arrays
arrays_list = []

# Iterate through the TIFF files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".tif"):
        file_path = os.path.join(folder_path, filename)
        
        # Open the TIFF file
        with rasterio.open(file_path) as src:
            # Read all bands of the TIFF file as a NumPy array
            array = src.read()
            
            # Add the array to the list
            arrays_list.append(array)

# Print the list of arrays
print(arrays_list)
```


d. The input image-patches numpy array now needs normalization. Create a function for this, and Display the min and max values in each band before and after normalization. 

```
import numpy as np

# Normalize each band of the image
normalized_images = np.zeros_like(images, dtype='float32')
for band in range(images.shape[1]):
    band_min = np.min(images[:, band])
    band_max = np.max(images[:, band])
    normalized_images[:, band] = (images[:, band] - band_min) / (band_max - band_min)
```


e. The input image-patches numpy array also needs to be reshaped from (no_of_images, channels, patch-size, patch-size) to (no_of_images, patch-size, patch-size, channels) that is compatabile to U-net input format. 

```
reshaped_images = normalized_images.reshape(-1, 256, 256, 8)
```

f. The label-patches numpy array needs one-hot encoding

```
from tensorflow.keras.utils import to_categorical

# Perform one-hot encoding on the labels
one_hot_labels = to_categorical(labels, num_classes=23)
```

g. A simple U-net function that can take in number of classes, patch size and build a tf model. Also define and understand various loss functions needed.

```
# https://youtu.be/jvZm8REF2KY
"""
Standard Unet
Model not compiled here, instead will be done externally to make it
easy to test various loss functions and optimizers. 
"""


from keras.models import Model
from keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D, concatenate, Conv2DTranspose, BatchNormalization, Dropout, Lambda
from keras import backend as K

def jacard_coef(y_true, y_pred):
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    return (intersection + 1.0) / (K.sum(y_true_f) + K.sum(y_pred_f) - intersection + 1.0)



################################################################
def multi_unet_model(n_classes=23, IMG_HEIGHT=256, IMG_WIDTH=256, IMG_CHANNELS=8):
#Build the model
    inputs = Input((IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS))
    #s = Lambda(lambda x: x / 255)(inputs)   #No need for this if we normalize our inputs beforehand
    s = inputs

    #Contraction path
    c1 = Conv2D(16, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(s)
    c1 = Dropout(0.2)(c1)  # Original 0.1
    c1 = Conv2D(16, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c1)
    p1 = MaxPooling2D((2, 2))(c1)
    
    c2 = Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(p1)
    c2 = Dropout(0.2)(c2)  # Original 0.1
    c2 = Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c2)
    p2 = MaxPooling2D((2, 2))(c2)
     
    c3 = Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(p2)
    c3 = Dropout(0.2)(c3)
    c3 = Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c3)
    p3 = MaxPooling2D((2, 2))(c3)
     
    c4 = Conv2D(128, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(p3)
    c4 = Dropout(0.2)(c4)
    c4 = Conv2D(128, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c4)
    p4 = MaxPooling2D(pool_size=(2, 2))(c4)
     
    c5 = Conv2D(256, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(p4)
    c5 = Dropout(0.3)(c5)
    c5 = Conv2D(256, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c5)
    
    #Expansive path 
    u6 = Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same')(c5)
    u6 = concatenate([u6, c4])
    c6 = Conv2D(128, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(u6)
    c6 = Dropout(0.2)(c6)
    c6 = Conv2D(128, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c6)
     
    u7 = Conv2DTranspose(64, (2, 2), strides=(2, 2), padding='same')(c6)
    u7 = concatenate([u7, c3])
    c7 = Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(u7)
    c7 = Dropout(0.2)(c7)
    c7 = Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c7)
     
    u8 = Conv2DTranspose(32, (2, 2), strides=(2, 2), padding='same')(c7)
    u8 = concatenate([u8, c2])
    c8 = Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(u8)
    c8 = Dropout(0.2)(c8)  # Original 0.1
    c8 = Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c8)
     
    u9 = Conv2DTranspose(16, (2, 2), strides=(2, 2), padding='same')(c8)
    u9 = concatenate([u9, c1], axis=3)
    c9 = Conv2D(16, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(u9)
    c9 = Dropout(0.2)(c9)  # Original 0.1
    c9 = Conv2D(16, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c9)
     
    outputs = Conv2D(n_classes, (1, 1), activation='softmax')(c9)
     
    model = Model(inputs=[inputs], outputs=[outputs])
    
    #NOTE: Compile the model in the main program to make it easy to test with various loss functions
    #model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    #model.summary()
    
    return model
 ```


h. Split the data into training and testing sets and train, and save the model. 

```
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(reshaped_images, one_hot_labels, test_size = 0.20, random_state = 42)

weights = [0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666,0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666]
dice_loss = sm.losses.DiceLoss(class_weights=weights) 
focal_loss = sm.losses.CategoricalFocalLoss()
total_loss = dice_loss + (1 * focal_loss)  #


IMG_HEIGHT = X_train.shape[1]
IMG_WIDTH  = X_train.shape[2]
IMG_CHANNELS = X_train.shape[3]


metrics=['accuracy', jacard_coef]


model = multi_unet_model(n_classes=23, IMG_HEIGHT=IMG_HEIGHT, IMG_WIDTH=IMG_WIDTH, IMG_CHANNELS=IMG_CHANNELS)


model.compile(optimizer='adam', loss=total_loss, metrics=metrics)
#model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=metrics)
model.summary()


history1 = model.fit(X_train, y_train, 
                    batch_size = 16, 
                    verbose=1, 
                    epochs=1, 
                    validation_data=(X_test, y_test), 
                    shuffle=False)

model.save('landcover_model.hdf5')

```

i. test the model and get metrics that are relevant to the segmentation.


j. perform a few sample prediction on the trained model and make original vs prediction. Remember to perform preprocessing steps like normalization, reshaping to the input image before feeding into the neural net. Also post processing steps such argmax is needed to see the output. Because the model outputs a numpy array of shape (1, 256, 256, 23), it indicates that the model predicts a segmentation mask for each pixel in the input images, where there are 23 classes. We need to first reshape it to (256,256,23) and then take argmax for each pixel to determine its class. 
```
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

with rasterio.open('/Users/srikarreddy/downloads/patch_106.tif') as src:
            # Read all bands of the TIFF file as a NumPy array
    new_array = src.read()

img = np.array(new_array)

import numpy as np

# Normalize each band of the image
large_img = np.zeros_like(img, dtype='float32')
for band in range(img.shape[1]):
    band_min = np.min(img[:, band])
    band_max = np.max(img[:, band])
    large_img[:, band] = (img[:, band] - band_min) / (band_max - band_min)

reshaped_image = large_img.reshape(-1, 256, 256, 8)
from keras.models import load_model
model = load_model("/Users/srikarreddy/downloads/landcover_model.hdf5", compile=False)
                  
# size of patches
patch_size = 256

# Number of classes 
n_classes = 23

output = model.predict(reshaped_image)

print(output.shape)

# Reshape the output array and take argmax to get the predicted class indices
segmentation_masks = output[0]
predicted_classes = np.argmax(segmentation_masks, axis=-1)

# Create a colormap for visualizing different classes
cmap = plt.get_cmap('tab20', segmentation_masks.shape[-1])

Visualize the segmentation mask
plt.imshow(predicted_classes, cmap=cmap)
plt.colorbar()
plt.title('Segmentation Mask')
plt.show()

# Save the segmentation mask as an image
output_image = Image.fromarray(np.uint8(predicted_classes))
output_image.save('/Users/srikarreddy/downloads/segmentation_mask.png')

```
6. Inference phase: Figure out a way to crop the big tif file and perform inference and stich them back up in an efficient way. 












