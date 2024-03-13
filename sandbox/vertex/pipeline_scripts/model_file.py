from tensorflow import keras
from tensorflow.keras import layers

def get_model(img_size, num_classes, num_bands=8):
    inputs = keras.Input(shape=img_size + (num_bands,))
    x = inputs

    # Encoder
    conv1 = layers.Conv2D(16, 3, activation="relu", padding="same")(x)
    conv1 = layers.Conv2D(16, 3, activation="relu", padding="same")(conv1)
    pool1 = layers.MaxPooling2D(pool_size=(2, 2))(conv1)

    conv2 = layers.Conv2D(32, 3, activation="relu", padding="same")(pool1)
    conv2 = layers.Conv2D(32, 3, activation="relu", padding="same")(conv2)
    pool2 = layers.MaxPooling2D(pool_size=(2, 2))(conv2)

    # Bottleneck
    conv3 = layers.Conv2D(64, 3, activation="relu", padding="same")(pool2)
    conv3 = layers.Conv2D(64, 3, activation="relu", padding="same")(conv3)

    # Decoder
    up4 = layers.UpSampling2D(size=(2, 2))(conv3)
    concat4 = layers.Concatenate()([up4, conv2])
    conv4 = layers.Conv2D(32, 3, activation="relu", padding="same")(concat4)
    conv4 = layers.Conv2D(32, 3, activation="relu", padding="same")(conv4)

    up5 = layers.UpSampling2D(size=(2, 2))(conv4)
    concat5 = layers.Concatenate()([up5, conv1])
    conv5 = layers.Conv2D(16, 3, activation="relu", padding="same")(concat5)
    conv5 = layers.Conv2D(16, 3, activation="relu", padding="same")(conv5)

    # Output
    outputs = layers.Conv2D(num_classes, 1, activation="softmax")(conv5)

    model = keras.Model(inputs, outputs)
    return model
