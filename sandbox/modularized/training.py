from image_clip import *
from model import *
from preprocessing import *
from sklearn.model_selection import train_test_split


datapath = '/home/otbuser/all/data/'

# image-clipping

# patches creation
training_images, height, width = preprocess_images(datapath, 'output.tif')
# masks creation
training_masks = preprocess_masks(datapath, 'crop_mask.tif', height, width)

# sampling the images and masks. Get the only useful masks and images
useful_training_images, useful_training_masks = sampling(training_images, training_masks)

# Model
model = multi_unet_model(n_classes=23, IMG_HEIGHT=256, IMG_WIDTH=256, IMG_CHANNELS=8)
model.summary()

X_train, X_test, y_train, y_test = train_test_split(useful_training_images,
                                                    useful_training_masks, test_size = 0.20, random_state = 42)


IMG_HEIGHT = X_train.shape[1]
IMG_WIDTH  = X_train.shape[2]
IMG_CHANNELS = X_train.shape[3]


metrics=['accuracy']


#model = multi_unet_model(n_classes=23, IMG_HEIGHT=IMG_HEIGHT, IMG_WIDTH=IMG_WIDTH, IMG_CHANNELS=IMG_CHANNELS)


model.compile(optimizer= tf.keras.optimizers.Adam(), loss=tf.keras.losses.CategoricalCrossentropy(), metrics=metrics)
model.summary()


history1 = model.fit(X_train, y_train,
                    batch_size = 16,
                    verbose=1,
                    epochs=30,
                    validation_data=(X_test, y_test),
                    shuffle=False)

model.save('/home/otbuser/all/code/model.hdf5')

