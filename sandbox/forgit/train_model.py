
import os
from build_features import *
import numpy as np
from sklearn.model_selection import train_test_split
from model import *
import tensorflow as tf


#-------------image preprocessing--------------------
patch_path = '/Users/srikarreddy/geosegment/data/sampled_patches/'
arrays_list = read_tiff_files_from_folder(patch_path)
images = np.array(arrays_list)
normalized_images = normalize_images(images)
patch_size = 256
num_bands = 8
reshaped_images = reshape_images(normalized_images, patch_size, num_bands)


#-----Labels preprocessing-------


label_path = '/Users/srikarreddy/geosegment/data/sampled_labels/'

arrays_list2 = read_tiff_files_from_folder(label_path)
number_of_labels = len(arrays_list2)

labels = np.array(arrays_list2)
labels = labels.reshape(number_of_labels, 256, 256)
print(labels.shape)

one_hot_labels = onehotencoding(labels)

#-----------test-train split------------

X_train, X_test, y_train, y_test = train_test_split(reshaped_images, 
                                                    one_hot_labels, test_size = 0.20, random_state = 42)


IMG_HEIGHT = X_train.shape[1]
IMG_WIDTH  = X_train.shape[2]
IMG_CHANNELS = X_train.shape[3]


metrics=['accuracy']


model = multi_unet_model(n_classes=23, IMG_HEIGHT=IMG_HEIGHT, IMG_WIDTH=IMG_WIDTH, IMG_CHANNELS=IMG_CHANNELS)


model.compile(optimizer= tf.keras.optimizers.Adam(), loss=tf.keras.losses.CategoricalCrossentropy(), metrics=metrics)
model.summary()


history1 = model.fit(X_train, y_train, 
                    batch_size = 16, 
                    verbose=1, 
                    epochs=100, 
                    validation_data=(X_test, y_test), 
                    shuffle=False)

model.save('/Users/srikarreddy/geosegment/models/0109_model.hdf5')