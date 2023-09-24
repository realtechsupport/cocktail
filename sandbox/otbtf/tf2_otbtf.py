import argparse
from pathlib import Path
import tensorflow as tf
import os
from otbtf.model import ModelBase
from otbtf import DatasetFromPatchesImages, TFRecords

#---Model-------------------------------------------------------------------------------
"""
Implementation of a small U-Net like model
"""

# Number of classes estimated by the model
N_CLASSES = 20

# Name of the input in the `FCNNModel` instance, also name of the input node
# in the SavedModel
INPUT_NAME = "input_xs"

# Name of the output in the `FCNNModel` instance
TARGET_NAME = "predictions"

# Name (prefix) of the output node in the SavedModel
OUTPUT_SOFTMAX_NAME = "predictions_softmax_tensor"


class FCNNModel(ModelBase):
    """
    A Simple Fully Convolutional U-Net like model
    """

    def normalize_inputs(self, inputs: dict):
        """
        Inherits from `ModelBase`

        The model will use this function internally to normalize its inputs,
        before applying `get_outputs()` that actually builds the operations
        graph (convolutions, etc). This function will hence work at training
        time and inference time.

        In this example, we assume that we have an input 12 bits multispectral
        image with values ranging from [0, 10000], that we process using a
        simple stretch to roughly match the [0, 1] range.

        Params:
            inputs: dict of inputs

        Returns:
            dict of normalized inputs, ready to be used from `get_outputs()`
        """
        return {INPUT_NAME: tf.cast(inputs[INPUT_NAME], tf.float32) * 0.0001}

    def get_outputs(self, normalized_inputs: dict) -> dict:
        """
        Inherits from `ModelBase`

        This small model produces an output which has the same physical
        spacing as the input. The model generates [1 x 1 x N_CLASSES] output
        pixel for [32 x 32 x <nb channels>] input pixels.

        Params:
            normalized_inputs: dict of normalized inputs

        Returns:
            dict of model outputs
        """

        norm_inp = normalized_inputs[INPUT_NAME]

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
        out_conv5 = _conv(norm_inp, 8, "conv5")
        out_conv1 = _conv(out_conv5, 16, "conv1")
        out_conv2 = _conv(out_conv1, 32, "conv2")
        out_conv3 = _conv(out_conv2, 64, "conv3")
        out_conv4 = _conv(out_conv3, 64, "conv4")
        out_tconv1 = _tconv(out_conv4, 64, "tconv1") + out_conv3
        out_tconv2 = _tconv(out_tconv1, 32, "tconv2") + out_conv2
        out_tconv3 = _tconv(out_tconv2, 16, "tconv3") + out_conv1
        out_tconv5 = _tconv(out_tconv3, 8, "tconv5") + out_conv5
        out_tconv4 = _tconv(out_tconv5, N_CLASSES, "classifier", None)

        # Replace the transposed convolutions with global average pooling
        gap = tf.keras.layers.GlobalAveragePooling2D(name="global_avg_pool")(out_tconv4)
        gap = tf.expand_dims(gap, axis=1)
        gap = tf.expand_dims(gap, axis=1)

        # Generally it is a good thing to name the final layers of the network
        # (i.e. the layers of which outputs are returned from
        # `MyModel.get_output()`). Indeed this enables to retrieve them for
        # inference time, using their name. In case your forgot to name the
        # last layers, it is still possible to look at the model outputs using
        # the `saved_model_cli show --dir /path/to/your/savedmodel --all`
        # command.
        #
        # Do not confuse **the name of the output layers** (i.e. the "name"
        # property of the tf.keras.layer that is used to generate an output
        # tensor) and **the key of the output tensor**, in the dict returned
        # from `MyModel.get_output()`. They are two identifiers with a
        # different purpose:
        #  - the output layer name is used only at inference time, to identify
        #    the output tensor from which generate the output image,
        #  - the output tensor key identifies the output tensors, mainly to
        #    fit the targets to model outputs during training process, but it
        #    can also be used to access the tensors as tf/keras objects, for
        #    instance to display previews images in TensorBoard.
        softmax_op = tf.keras.layers.Softmax(name=OUTPUT_SOFTMAX_NAME)
        predictions = softmax_op(gap)
        #print(predictions.shape)

        return {TARGET_NAME: predictions}


def dataset_preprocessing_fn(examples: dict):
    """
    Preprocessing function for the training dataset.
    This function is only used at training time, to put the data in the
    expected format for the training step.
    DO NOT USE THIS FUNCTION TO NORMALIZE THE INPUTS ! (see
    `otbtf.ModelBase.normalize_inputs` for that).
    Note that this function is not called here, but in the code that prepares
    the datasets.

    Params:
        examples: dict for examples (i.e. inputs and targets stored in a single
            dict)

    Returns:
        preprocessed examples

    """

    return {
        INPUT_NAME: examples["input_xs_patches"],
        TARGET_NAME: tf.one_hot(
            tf.squeeze(tf.cast(examples["labels_patches"], tf.int32), axis=-1),
            depth=N_CLASSES
        )
    }


def train(model_dir, batch_size, learning_rate, nb_epochs, ds_train, ds_valid, ds_test):
    """
    Create, train, and save the model.

    Params:
        params: contains batch_size, learning_rate, nb_epochs, and model_dir
        ds_train: training dataset
        ds_valid: validation dataset
        ds_test: testing dataset

    """

    strategy = tf.distribute.MirroredStrategy()  # For single or multi-GPUs
    with strategy.scope():
        # Model instantiation. Note that the normalize_fn is now part of the
        # model. It is mandatory to instantiate the model inside the strategy
        # scope.
        model = FCNNModel(dataset_element_spec=ds_train.element_spec)

        # Compile the model
        model.compile(
            loss=tf.keras.losses.CategoricalCrossentropy(),
            optimizer=tf.keras.optimizers.Adam(
                learning_rate=learning_rate
            ),
            metrics=[tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
        )

        # Summarize the model (in CLI)
        model.summary()

        # Train
        model.fit(ds_train, epochs=nb_epochs, validation_data=ds_valid)

        # Evaluate against test data
        if ds_test is not None:
            model.evaluate(ds_test, batch_size=batch_size)

        # Save trained model as SavedModel
        model.save(model_dir)




#---Create TFRecords--------------------------------------------------------------------

def create_tfrecords(patches, labels, outdir):
    patches = sorted(patches)
    labels = sorted(labels)
    outdir = Path(outdir)
    if not outdir.exists():
        outdir.mkdir(exist_ok=True)
    #create a dataset
    dataset = DatasetFromPatchesImages(
        filenames_dict = {
            "input_xs_patches":patches,
            "labels_patches": labels
        }
    )
    #convert dataset into TFRecords
    dataset.to_tfrecords(output_dir=outdir, drop_remainder=False)

#----Main------------------------------------------------------------
if __name__=="__main__":
    datapath = "/home/otbuser/all/data/"
    batch_size = 8
    learning_rate = 0.0001
    nb_epochs = 5

    # create TFRecords
    patches = ['/home/otbuser/all/data/area2_0530_2022_8bands_patches_A.tif', '/home/otbuser/all/data/area2_0530_2022_8bands_patches_B.tif']
    labels = ['/home/otbuser/all/data/area2_0530_2022_8bands_labels_A.tif', '/home/otbuser/all/data/area2_0530_2022_8bands_labels_B.tif']
    create_tfrecords(patches=patches[0:1], labels=labels[0:1], outdir=datapath+"train")
    create_tfrecords(patches=patches[1:], labels=labels[1:], outdir=datapath+"valid")

    # Train the model and save the model
    train_dir = os.path.join(datapath, "train")
    valid_dir = os.path.join(datapath, "valid")
    test_dir = None # define the training directory if test dataset is available
    kwargs = {
        "batch_size": batch_size,
        "target_keys": [TARGET_NAME],
        "preprocessing_fn": dataset_preprocessing_fn
    }
    #shuffle_buffer_size=1000,
    ds_train = TFRecords(train_dir).read(**kwargs)
    ds_valid = TFRecords(valid_dir).read(**kwargs)

    

    train(datapath+"sandbox_model", batch_size, learning_rate, nb_epochs, ds_train, ds_valid, ds_test=None)


