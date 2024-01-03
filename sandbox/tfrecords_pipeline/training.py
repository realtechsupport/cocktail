from tensorflow import keras
from tensorflow.keras import layers
import os
import tensorflow as tf
from model import get_model
from create_dataset import train_test_datasets

# values
num_bands = 8 # 8 bands images as input 
patch_height = 8
patch_width = 8
img_size = (patch_height, patch_width)
num_classes = 23
path = '/home/otbuser/all/code/'

# get the train and test datasets
train_dataset, val_dataset = train_test_datasets()
model = get_model(img_size=img_size, num_classes=num_classes, num_bands=num_bands)
model.compile(optimizer="adam", loss="categorical_crossentropy")
callbacks = [
    keras.callbacks.ModelCheckpoint(path+"patch_8_batch_32.hdf5",
                                    save_best_only=True)
]
model_history = model.fit(train_dataset,
                    epochs=25,
                    callbacks=callbacks,
                    batch_size=32,
                    validation_data= val_dataset)
model.save(path+'patch_8_batch_32.hdf5')






