from sklearn.model_selection import train_test_split

# importing user defined libraries 
from model import * 
from dataprep import *

# code for inputs variables
# code for getting the reshaped_images
# code for one-hot encoded labels
#--------Inputs-----
datapath = '/home/otbuser/all/data/'
input_image_path = 'area2_0530_2022_8bands.tif'    
crop_size = 256
cropped_image = 'cropped_input.tif'
crop_to_nearest_patch_size(datapath, input_image_path, crop_size, cropped_image)

patch_path = '/home/otbuser/all/data/patches/'

patch_size = (256, 256)

extract_and_save_patches(datapath, patch_path, cropped_image, patch_size)

arrays_list = read_tiff_files_from_folder(patch_path)

images = np.array(arrays_list)

normalized_images = normalize_images(images)

p_size1 = 256
p_size2 = 256
num_bands = 8
reshaped_images = reshape_images(normalized_images, p_size1, p_size2, num_bands)

#-----Labels-------
label_image_path = 'OUTPUT.tif'    
cropped_label = 'cropped_label.tif'
crop_to_nearest_patch_size(datapath, label_image_path, crop_size, cropped_label)

label_path = '/home/otbuser/all/data/labels/'



extract_and_save_patches(datapath, label_path, cropped_label, patch_size)

arrays_list2 = read_tiff_files_from_folder(label_path)

labels = np.array(arrays_list2)
print(labels.shape)


one_hot_labels = onehotencoding(labels)


#------------------------------------------------------------------------Train--------------------------
X_train, X_test, y_train, y_test = train_test_split(reshaped_images, one_hot_labels, test_size = 0.20, random_state = 42)

# 
weights = [0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666,0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666, 0.1666]
# dice_loss = sm.losses.DiceLoss(class_weights=weights) 
# focal_loss = sm.losses.CategoricalFocalLoss()
# total_loss = dice_loss + (1 * focal_loss)  #


IMG_HEIGHT = X_train.shape[1]
IMG_WIDTH  = X_train.shape[2]
IMG_CHANNELS = X_train.shape[3]


metrics=['accuracy', jacard_coef]


model = multi_unet_model(n_classes=23, IMG_HEIGHT=IMG_HEIGHT, IMG_WIDTH=IMG_WIDTH, IMG_CHANNELS=IMG_CHANNELS)


model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=metrics)
#model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=metrics)
model.summary()


history1 = model.fit(X_train, y_train, 
                    batch_size = 16, 
                    verbose=1, 
                    epochs=1, 
                    validation_data=(X_test, y_test), 
                    shuffle=False)

model.save('landcover_model.hdf5')