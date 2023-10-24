from datapreprocessing import *
from model import *
import numpy as np
import random
import matplotlib.pyplot as plt
import sys, os
from google.cloud import storage
from downloadImages import *

# download the images to local folder
bucket_name = 'gislogics-bucket'
source_folder = 'area2_planetlabs_superdove/'
destination_folder = '/home/otbuser/all/data/images/'

download_files_from_gcs(bucket_name, source_folder, destination_folder)

# perform the clipping on one image
datapath1 = '/home/otbuser/all/data/'
ps = 'crop_mask.tif'
patch_size = 256
roipath = '/home/otbuser/all/data/roi_folder/'
roishape = 'area2_square.geojson'
clipping(datapath1, ps, roipath, roishape)
datapath = '/home/otbuser/all/data/images/'


# get the preprocessed target
new_roi_file = '/home/otbuser/all/data/roi_folder/crop_mask_roi.tif'
target = target_preprocessing(new_roi_file, patch_size)


# create a dataset
dataset = process_images_in_folder(datapath, patch_size, roipath, target)

# training
img_size = (256, 256)
num_classes = 21
model = get_model(img_size=img_size, num_classes=num_classes)
print(model.summary())
num_imgs = len(dataset[1])

input_img_paths = dataset[0]
target_paths = dataset[1]

print(input_img_paths[0].shape)
print(target_paths[0].shape)

random.Random(1337).shuffle(input_img_paths)
random.Random(1337).shuffle(target_paths)


input_imgs = np.zeros((num_imgs,) + img_size + (8,), dtype="float32")
targets = np.zeros((num_imgs,) + img_size + (21,), dtype="uint8")

for i in range(num_imgs):

    input_imgs[i] = input_img_paths[i]
    targets[i] = target_paths[i]

num_val_samples = round(0.2 * num_imgs)

train_input_imgs = input_imgs[:-num_val_samples]
train_targets = targets[:-num_val_samples]

val_input_imgs = input_imgs[-num_val_samples:]
val_targets = targets[-num_val_samples:]


model.compile(optimizer="rmsprop", loss="categorical_crossentropy")

callbacks = [
    keras.callbacks.ModelCheckpoint("new_segmentation.hdf5",
                                    save_best_only=True)
]

history = model.fit(train_input_imgs, train_targets,
                    epochs=5,
                    callbacks=callbacks,
                    batch_size=8,
                    validation_data=(val_input_imgs, val_targets))

model.save('/home/otbuser/all/code/multi_image_model.hdf5')

# visualization of training loss
epochs = range(1, len(history.history["loss"]) + 1)
loss = history.history["loss"]
val_loss = history.history["val_loss"]
plt.figure()
plt.plot(epochs, loss, "bo", label="Training loss")
plt.plot(epochs, val_loss, "b", label="Validation loss")
plt.title("Training and validation loss")
plt.legend()
plt.savefig('/home/otbuser/all/data/Training-and-validation-loss.png')




