from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.utils import plot_model
import matplotlib.pyplot as plt


class CustomModel:
    def __init__(
        self,
        img_size,
        num_classes,
        num_bands=8,
        num_unet_layers=4,
        use_early_stopping=False,
        dropout_rate=None,
        transfer_learning_model=None,
    ):
        self.img_size = img_size
        self.num_classes = num_classes
        self.num_bands = num_bands
        self.num_unet_layers = num_unet_layers
        self.use_early_stopping = use_early_stopping
        self.dropout_rate = dropout_rate
        self.transfer_learning_model = transfer_learning_model
        self.model = self.build_model()

    def build_model(self):
        if self.transfer_learning_model is not None:
            return self.build_transfer_learning_model()
        else:
            ## we can actually build unet++ with skip connections.
            ## but first let's put some check in u net model to not give any error.
            return self.build_unet_model()

    def build_unet_model(self):
        if self.img_size[0] // (2 ** self.num_unet_layers) < 2 or self.img_size[1] // (2 ** self.num_unet_layers) < 2:
            raise ValueError(f"Image size is too small for the specified number of UNET layers. Cannot build the model.")
        inputs = keras.Input(shape=self.img_size + (self.num_bands,))
        x = inputs

        # Encoder
        for _ in range(self.num_unet_layers):
            x = layers.Conv2D(16, 3, activation="relu", padding="same")(x)
            x = layers.Conv2D(16, 3, activation="relu", padding="same")(x)
            x = layers.MaxPooling2D(pool_size=(2, 2))(x)

        # Bottleneck
        for _ in range(self.num_unet_layers):
            x = layers.Conv2D(64, 3, activation="relu", padding="same")(x)
            x = layers.Conv2D(64, 3, activation="relu", padding="same")(x)

        # Decoder
        for _ in range(self.num_unet_layers):
            x = layers.UpSampling2D(size=(2, 2))(x)
            x = layers.Concatenate()(
                [x, layers.Conv2D(16, 3, activation="relu", padding="same")(x)]
            )
            x = layers.Conv2D(16, 3, activation="relu", padding="same")(x)
            x = layers.Conv2D(16, 3, activation="relu", padding="same")(x)

        # Output
        outputs = layers.Conv2D(self.num_classes, 1, activation="softmax")(x)

        model = keras.Model(inputs, outputs)

        if self.use_early_stopping:
            pass

        if self.dropout_rate is not None:
            model.add(layers.Dropout(self.dropout_rate))

        return model

    def build_transfer_learning_model(self):
        ## transfer learning should not be trainable.
        ## But it should have an option to finetune the head.
        for layer in self.transfer_learning_model.layers[:-1]:
            layer.trainable = False

        x = layers.GlobalAveragePooling2D()(
            self.transfer_learning_model.layers[-2].output
        )
        outputs = layers.Dense(self.num_classes, activation="softmax")(x)
        model = keras.Model(self.transfer_learning_model.input, outputs)
        return model

    def plot_model_diagram(self, file_path):
        plot_model(
            self.model, to_file=file_path, show_shapes=True, show_layer_names=True
        )
        img = plt.imread(file_path)
        plt.figure(figsize=(10, 10))
        plt.imshow(img)
        plt.axis("off")
        plt.show()
