
from tensorflow.keras.layers import Input, Conv2D, Dropout, Conv2DTranspose, UpSampling2D, concatenate

def r_multi_unet_model(n_classes=21, IMG_HEIGHT=16, IMG_WIDTH=16, IMG_CHANNELS=8):
  # Build the model
  inputs = Input((IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS))

  # Contraction path
  c1 = Conv2D(16, (3, 3), activation='relu', padding='same')(inputs)
  c1 = Dropout(0.2)(c1)
  c1 = Conv2D(16, (3, 3), activation='relu', padding='same')(c1)

  # Use strided convolutions instead of pooling
  c2 = Conv2D(32, (3, 3), strides=(2, 2), activation='relu', padding='same')(c1)
  c2 = Dropout(0.2)(c2)
  c2 = Conv2D(32, (3, 3), activation='relu', padding='same')(c2)

  c3 = Conv2D(64, (3, 3), strides=(2, 2), activation='relu', padding='same')(c2)
  c3 = Dropout(0.2)(c3)
  c3 = Conv2D(64, (3, 3), activation='relu', padding='same')(c3)

  c4 = Conv2D(128, (3, 3), strides=(2, 2), activation='relu', padding='same')(c3)
  c4 = Dropout(0.2)(c4)
  c4 = Conv2D(128, (3, 3), activation='relu', padding='same')(c4)

  c5 = Conv2D(256, (3, 3), activation='relu', padding='same')(c4)
  c5 = Dropout(0.3)(c5)
  c5 = Conv2D(256, (3, 3), activation='relu', padding='same')(c5)

  # Expansive path
  u6 = Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same')(c5)
  c4_up = UpSampling2D(size=(2, 2))(c4)  # Upsample c4 to match u6 dimensions
  u6 = concatenate([u6, c4_up], axis=3)
  c6 = Conv2D(128, (3, 3), activation='relu', padding='same')(u6)
  c6 = Dropout(0.2)(c6)
  c6 = Conv2D(128, (3, 3), activation='relu', padding='same')(c6)

  u7 = Conv2DTranspose(64, (2, 2), strides=(2, 2), padding='same')(c6)
  c3_up = UpSampling2D(size=(2, 2))(c3)  # Upsample c3 to match u7 dimensions
  u7 = concatenate([u7, c3_up], axis=3)
  c7 = Conv2D(64, (3, 3), activation='relu', padding='same')(u7)
  c7 = Dropout(0.2)(c7)
  c7 = Conv2D(64, (3, 3), activation='relu', padding='same')(c7)

  u8 = Conv2DTranspose(32, (2, 2), strides=(2, 2), padding='same')(c7)
  c2_up = UpSampling2D(size=(2, 2))(c2)  # Upsample c2 to match u8 dimensions
  u8 = concatenate([u8, c2_up], axis=3)
  c8 = Conv2D(32, (3, 3), activation='relu', padding='same')(u8)
  c8 = Dropout(0.2)(c8)
  c8 = Conv2D(32, (3, 3), activation='relu', padding='same')(c8)

  # Output layer
  outputs = Conv2D(n_classes, (1, 1), activation='softmax')(c8)  
    
  model = Model(inputs=[inputs], outputs=[outputs])
  return model
 
