from otbtf import DatasetFromPatchesImages
from otbtf import TFRecords
import tensorflow as tf
from otbtf import ModelBase

print("working")

dataset = DatasetFromPatchesImages(
    filenames_dict={
        "input_xs_patches": ['/home/otbuser/all/data/area2_0530_2022_8bands_patches_A.tif'],
        "labels_patches": "D:\OneDrive - University at Buffalo\Projects\GeoAI\cocktail\data\new_data\area2_0530_2022_8bands.tif"']   #write the actual file name
    }
)

tf_dataset = dataset.get_tf_dataset(
    batch_size=8,
    targets_keys=["predictions"]
)

dataset.to_tfrecords(output_dir="/home/otbuser/all/data/tmp/")

dataset = TFRecords("/home/otbuser/all/data/tmp/")
tf_dataset = dataset.read(
    shuffle_buffer_size=1000,
    batch_size=8,
    target_keys=["predictions"]
)

# Number of classes estimated by the model
N_CLASSES = 20 #change the number to actual

# Name of the input
INPUT_NAME = "input_xs_patches"

# Name of the target output
TARGET_NAME = "predictions"

# Name (prefix) of the output we will use at inference time
OUTPUT_SOFTMAX_NAME = "predictions_softmax_tensor"

def dataset_preprocessing_fn(examples):
    return {
        INPUT_NAME: examples["input_xs_patches"],
        TARGET_NAME: tf.one_hot(
            tf.squeeze(tf.cast(examples["labels_patches"], tf.int32), axis=-1),
            depth=N_CLASSES
        )
    }

class FCNNModel(ModelBase):
    def normalize_inputs(self, inputs):
        return {INPUT_NAME: tf.cast(inputs[INPUT_NAME], tf.float32) * 0.0001}
    def get_outputs(self, normalized_inputs):

        def _conv(inp, depth, name):
            conv_op = tf.keras.layers.Conv2D(
                filters=depth,
                kernel_size=3,
                strides=2,
                activation="relu",
                padding="same",
                name=name
            )
            return conv_op(inp)

        def _tconv(inp, depth, name, activation="relu"):
            tconv_op = tf.keras.layers.Conv2DTranspose(
                filters=depth,
                kernel_size=3,
                strides=2,
                activation=activation,
                padding="same",
                name=name
            )
            return tconv_op(inp)

        out_conv1 = _conv(normalized_inputs[INPUT_NAME], 16, "conv1")
        out_conv2 = _conv(out_conv1, 32, "conv2")
        out_conv3 = _conv(out_conv2, 64, "conv3")
        out_conv4 = _conv(out_conv3, 64, "conv4")
        out_tconv1 = _tconv(out_conv4, 64, "tconv1") + out_conv3
        out_tconv2 = _tconv(out_tconv1, 32, "tconv2") + out_conv2
        out_tconv3 = _tconv(out_tconv2, 16, "tconv3") + out_conv1
        out_tconv4 = _tconv(out_tconv3, N_CLASSES, "classifier", None)

        softmax_op = tf.keras.layers.Softmax(name=OUTPUT_SOFTMAX_NAME)
        predictions = softmax_op(out_tconv4)

        return {TARGET_NAME: predictions}

strategy = tf.distribute.MirroredStrategy()

with strategy.scope():
    model = FCNNModel(dataset_element_spec=tf_dataset.element_spec)

    model.compile(
        loss=tf.keras.losses.CategoricalCrossentropy(),
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        metrics=[tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
    )
    model.fit(tf_dataset, epochs=100, validation_data=tf_dataset)

    model.evaluate(tf_dataset, batch_size=64)

    model.save("/home/otbuser/all/data/tmp/my_1st_savedmodel")


