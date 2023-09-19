import os
import numpy as np
#import glob
import numpy as np
from matplotlib import pyplot as plt
#from patchify import patchify
#import tifffile as tiff
#from PIL import Image
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.metrics import MeanIoU
import random
import rasterio 
from rasterio.windows import Window
from tensorflow.keras.utils import to_categorical
import shutil
from pathlib import Path
from sklearn.metrics import confusion_matrix




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
 

label_path = '/home/otbuser/all/data/labels/'
output_folder = '/home/otbuser/all/data/sampled_labels'

sampling(label_path,output_folder)

def copy_file_with_number(filename, source_folder, target_folder):
    # Get the number from the input filename
    number = ''.join(filter(str.isdigit, filename))
    
    # Search for a file with the same number in the source folder
    for source_file in Path(source_folder).glob(f'*{number}*'):
        if source_file.is_file():
            Path(target_folder).mkdir(parents=True, exist_ok=True)
            # Construct the target file path in the target folder
            target_file = Path(target_folder) / source_file.name

            # Copy the source file to the target folder
            shutil.copyfile(source_file, target_file)

            print(f"File copied: {source_file} -> {target_file}")
            return
    
    print(f"No file with number {number} found in the source folder.")

# Example usage
source_folder = '/home/otbuser/all/data/patches/'
target_folder = '/home/otbuser/all/data/sampled_patches/'

for filename in os.listdir(output_folder):
    copy_file_with_number(filename, source_folder, target_folder)


from sklearn.model_selection import train_test_split

# importing user defined libraries 
from model import * 
from dataprep import *

patch_path = '/home/otbuser/all/data/sampled_patches/'
label_path = '/home/otbuser/all/data/sampled_labels/' 
arrays_list = read_tiff_files_from_folder(patch_path)

images = np.array(arrays_list)

normalized_images = normalize_images(images)

p_size1 = 256
p_size2 = 256
num_bands = 8
reshaped_images = reshape_images(normalized_images, p_size1, p_size2, num_bands)



arrays_list2 = read_tiff_files_from_folder(label_path)

labels = np.array(arrays_list2)
labels = labels.reshape(33, 256, 256)
print(labels.shape)


one_hot_labels = onehotencoding(labels)



X_train, X_test, y_train, y_test = train_test_split(reshaped_images, one_hot_labels, test_size = 0.20, random_state = 42)

IMG_HEIGHT = X_train.shape[1]
IMG_WIDTH  = X_train.shape[2]
IMG_CHANNELS = X_train.shape[3]


metrics=['accuracy', jacard_coef]


model = multi_unet_model(n_classes=23, IMG_HEIGHT=IMG_HEIGHT, IMG_WIDTH=IMG_WIDTH, IMG_CHANNELS=IMG_CHANNELS)


#model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=metrics)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=metrics)
model.summary()


history1 = model.fit(X_train, y_train, 
                    batch_size = 16, 
                    verbose=1, 
                    epochs=10, 
                    validation_data=(X_test, y_test), 
                    shuffle=False)


def calculate_confusion_matrix(predictions, ground_truth, num_classes):
    conf_matrix = [[0] * num_classes for _ in range(num_classes)]

    for i in range(predictions.shape[0]):
        for j in range(predictions.shape[1]):
            for k in range(predictions.shape[2]):
                pred_class = predictions[i, j, k]
                true_class = ground_truth[i, j, k]
                conf_matrix[true_class][pred_class] += 1

    return conf_matrix



# Predict on the test data
y_pred = model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=-1)
y_true_classes = np.argmax(y_test, axis=-1)

# Calculate the confusion matrix
confusion_mtx = calculate_confusion_matrix(y_true_classes, y_pred_classes)

# Define class labels (assuming you have 23 classes)
class_labels = [str(i) for i in range(23)]

# Plot the confusion matrix
plt.figure(figsize=(10, 8))
plt.imshow(confusion_mtx, interpolation='nearest', cmap=plt.cm.Blues)
plt.title('Confusion Matrix')
plt.colorbar()
plt.xticks(np.arange(len(class_labels)), class_labels, rotation=45)
plt.yticks(np.arange(len(class_labels)), class_labels)
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.tight_layout()
plt.show()


model.save('sampled_landcover_model.hdf5')
