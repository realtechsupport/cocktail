# 92% of storage used … If you run out, you won't have enough storage to create, edit and upload files. Get 100 GB of storage for ₹130.00 ₹35.00/month for 3 months.
# Testing data preparation for  ingestion into OTBTF deeplearning
# otbf_main.py
# July 2023
#--------------------------------------------------------
# Reference
# https://forgemia.inra.fr/remi.cresson/otbtf/-/blob/c7a36485a31b86048bd3280f0731944d2dbdad47/test/tutorial_unittest.py
# https://otbtf.readthedocs.io/en/latest/app_sampling.html#patchesselection
# -------------------------------------------------------
import argparse
from pathlib import Path
from tensorflow.keras.utils import plot_model


import os, sys
import time
import numpy as np

import tensorflow as tf


import otbtf
import otbApplication

import otbtf.tfrecords
import otbtf.utils

from osgeo import gdal
from otbtf import DatasetFromPatchesImages, TFRecords
from otbtf.model import ModelBase
from otbtf import TFRecords
from otbtf.examples.tensorflow_v2x.fcnn import fcnn_model
from otbtf.examples.tensorflow_v2x.fcnn import helper

from tricks import *
from osgeo import gdal

# home made
from helper import *
from otbtf_helper import *

datapath = "/home/otbuser/all/data/"
print("datapath: ", datapath)

# ------------------------------------------------------------------------------
# Ensure that the input image is normalized before proceeding with the next steps
input = 'area2_0530_2022_8bands.tif'
normalized_input = 'area2_0530_2022_8bands_norm.tif'
scale_min = 0
scale_max = 65535
# print(input.shape, normalized_input.shape)

scale_and_normalize(datapath, input, normalized_input, scale_min, scale_max)
print("\nImage normalized")
# ------------------------------------------------------------------------------
# input = normalized_input                # use the normalized input !! 

out_patches_A = input.split('.')[0] + "_patches_A.tif"
out_labels_A = input.split('.')[0] + "_labels_A.tif"

out_patches_B = input.split('.')[0] + "_patches_B.tif"
out_labels_B = input.split('.')[0] + "_labels_B.tif"

#--------------------------------------------------------------------------------
apptype = "PolygonClassStatistics"
vec = "area2_0123_2023_raster_classification_13.shp"
output = "area2_0123_2023_raster_classification_13_vecstats.xml"

PolygonClassStatistics(apptype, datapath, input, vec, output)
print("\Stats created")
#------------------------------------------------------------------------------
apptype = "SampleSelection"
instats = "area2_0123_2023_raster_classification_13_vecstats.xml"
output_A = "area2_0123_2023_raster_classification_13_points_A.shp"
output_B = "area2_0123_2023_raster_classification_13_points_B.shp"

SampleSelection(apptype, datapath, input, vec, instats, output_A)
print("\nSamples A created")
SampleSelection(apptype, datapath, input, vec, instats, output_B)
print("\nSamples B created")
#------------------------------------------------------------------------------
out_patches_A = input.split('.')[0] + "_patches_A.tif"
out_labels_A = input.split('.')[0] + "_labels_A.tif"

out_patches_B = input.split('.')[0] + "_patches_B.tif"
out_labels_B = input.split('.')[0] + "_labels_B.tif"
#------------------------------------------------------------------------------
apptype = "PatchesExtraction"
patchsize = 64 		#16?
vec_A = output_A
vec_B = output_B

PatchesExtraction(apptype, datapath, input, vec_A, out_patches_A, out_labels_A, patchsize)
print("\nPatches A created")
PatchesExtraction(apptype, datapath, input, vec_B, out_patches_B, out_labels_B, patchsize)
print("\nPatches B created")
#----------------------------------------------------------------------------

# call create model
# call model train
# call model test







#---Model-------------------------------------------------------------------------------
# """
# Implementation of a small U-Net like model
# """

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
        # gap = out_tconv4
        # Replace the transposed convolutions with global average pooling
        gap = tf.keras.layers.GlobalAveragePooling2D(name="global_avg_pool")(out_tconv4)
        gap = tf.expand_dims(gap, axis=1)
        gap = tf.expand_dims(gap, axis=1)

        print("Batch size:", gap.shape[0])
        print("Height:", gap.shape[1])
        print("Width:", gap.shape[2])
        print("Channels:", gap.shape[3])


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
        
        # *****************************************************************************
        # i'm changing it to tf.argmax rather than np.argmax, because it was giving error
        predictions = tf.argmax(predictions)
        # *****************************************************************************
        # print(predictions.shape)

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

        # tf.keras.utils.plot_model(
        #     model,
        #     show_shapes=True,
        #     to_file='model.png')

        # Train
        model.fit(ds_train, epochs=nb_epochs, validation_data=ds_valid)

        # Evaluate against test data
        if ds_test is not None:
            model.evaluate(ds_test, batch_size=batch_size)

        # Save trained model as SavedModel
        model.save(model_dir)




# ________________________________________________________________________________________
# ****************************************************************************************
# ****************************************************************************************
# ________________________________________________________________________________________

# Let's try to copy otbtf code and change it so it would run maybe.
# from this line onwards everything has been copied from remicres

# class Dataset:
#     """
#     Handles the "mining" of patches.
#     This class has a thread that extract tuples from the readers, while
#     ensuring the access of already gathered tuples.

#     See `PatchesReaderBase` and `Buffer`

#     """

#     def __init__(
#             self,
#             patches_reader: PatchesReaderBase = None,
#             buffer_length: int = 128,
#             iterator_cls: Type[IteratorBase] = RandomIterator,
#             max_nb_of_samples: int = None
#     ):
#         """
#         Params:
#             patches_reader: The patches reader instance
#             buffer_length: The number of samples that are stored in the
#                 buffer
#             iterator_cls: The iterator class used to generate the sequence of
#                 patches indices.
#             max_nb_of_samples: Optional, max number of samples to consider

#         """
#         # patches reader
#         self.patches_reader = patches_reader

#         # If necessary, limit the nb of samples
#         logging.info('Number of samples: %s', self.patches_reader.get_size())
#         if max_nb_of_samples and \
#                 self.patches_reader.get_size() > max_nb_of_samples:
#             logging.info('Reducing number of samples to %s', max_nb_of_samples)
#             self.size = max_nb_of_samples
#         else:
#             self.size = self.patches_reader.get_size()

#         # iterator
#         self.iterator = iterator_cls(patches_reader=self.patches_reader)

#         # Get patches sizes and type, of the first sample of the first tile
#         self.output_types = {}
#         self.output_shapes = {}
#         one_sample = self.patches_reader.get_sample(index=0)
#         for src_key, np_arr in one_sample.items():
#             self.output_shapes[src_key] = np_arr.shape
#             self.output_types[src_key] = tf.dtypes.as_dtype(np_arr.dtype)

#         logging.info("output_types: %s", self.output_types)
#         logging.info("output_shapes: %s", self.output_shapes)

#         # buffers
#         if self.size <= buffer_length:
#             buffer_length = self.size
#         self.miner_buffer = Buffer(buffer_length)
#         self.mining_lock = multiprocessing.Lock()
#         self.consumer_buffer = Buffer(buffer_length)
#         self.consumer_buffer_pos = 0
#         self.tot_wait = 0
#         self.miner_thread = self._summon_miner_thread()
#         self.read_lock = multiprocessing.Lock()
#         self._dump()

#         # Prepare tf dataset for one epoch
#         self.tf_dataset = tf.data.Dataset.from_generator(
#             self._generator,
#             output_types=self.output_types,
#             output_shapes=self.output_shapes
#         ).repeat(1)

#     def to_tfrecords(
#             self,
#             output_dir: str,
#             n_samples_per_shard: int = 100,
#             drop_remainder: bool = True
#     ):
#         """
#         Save the dataset into TFRecord files

#         Params:
#             output_dir: output directory
#             n_samples_per_shard: number of samples per TFRecord file
#             drop_remainder: drop remaining samples

#         """
#         tfrecord = otbtf.tfrecords.TFRecords(output_dir)
#         tfrecord.ds2tfrecord(
#             self,
#             n_samples_per_shard=n_samples_per_shard,
#             drop_remainder=drop_remainder
#         )

# class TFRecords:
#     """
#     This class allows to convert Dataset objects to TFRecords and to load them
#     in dataset tensorflow format.
#     """

#     def __init__(self, path: str):
#         """
#         Params:
#             path: Can be a directory where TFRecords must be saved/loaded
#         """
#         self.dirpath = path
#         os.makedirs(self.dirpath, exist_ok=True)
#         self.output_types_file = os.path.join(
#             self.dirpath, "output_types.json"
#         )
#         self.output_shapes_file = os.path.join(
#             self.dirpath, "output_shapes.json"
#         )
#         self.output_shapes = self.load(self.output_shapes_file) \
#             if os.path.exists(self.output_shapes_file) else None
#         self.output_types = self.load(self.output_types_file) \
#             if os.path.exists(self.output_types_file) else None

#     @staticmethod
#     def _bytes_feature(value):
#         """
#         Convert a value to a type compatible with tf.train.Example.

#         Params:
#             value: value

#         Returns:
#             a bytes_list from a string / byte.
#         """
#         if isinstance(value, type(tf.constant(0))):
#             value = value.numpy()  # BytesList won't unpack a string from
#             # an EagerTensor.
#         return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))




#---Create TFRecords--------------------------------------------------------------------

def create_tfrecords(patches, labels, outdir):
    
    patches = sorted(patches)
    labels = sorted(labels)
    outdir = Path(outdir)
    if not outdir.exists():
        outdir.mkdir(exist_ok=True)

    # print(patches[0].type)
    # # we are sending the string, it is sorting and doing everything in the backend

    # # Convert patches and labels to NumPy arrays or byte strings
    # patches = [p.numpy() if isinstance(p, tf.Tensor) else p for p in patches]
    # labels = [l.numpy() if isinstance(l, tf.Tensor) else l for l in labels]


    # Create placeholders for patches and labels
    # patches_placeholder = tf.placeholder(tf.float32, shape=(None,))  # Modify the data type as needed
    # labels_placeholder = tf.placeholder(tf.float32, shape=(None,))   # Modify the data type as needed

    #create a dataset
    dataset = DatasetFromPatchesImages(
        filenames_dict = {
            "input_xs_patches":patches,
            "labels_patches": labels
        }
    )

    is_eager_execution = tf.executing_eagerly()
    print('Is eager execution:', is_eager_execution)

    # with tf.compat.v1.enable_eager_execution() as sess:
    #     # Initialize variables if needed
    #     sess.run(tf.global_variables_initializer())

        # Feed the data into the placeholders
        # feed_dict = {
        #     patches_placeholder: np.array(patches),  # Convert patches to NumPy array
        #     labels_placeholder: np.array(labels)    # Convert labels to NumPy array
        # }

        # Convert dataset into TFRecords
        # dataset.to_tfrecords(output_dir=outdir, drop_remainder=False)
    # #convert dataset into TFRecords
    dataset.to_tfrecords(output_dir=outdir, drop_remainder=False)

#----Main------------------------------------------------------------
if __name__=="__main__":
    datapath = "/home/otbuser/all/data/"
    batch_size = 8
    learning_rate = 0.0001
    nb_epochs = 5

    # create TFRecords
    tf.compat.v1.enable_eager_execution()
    patches = ['/home/otbuser/all/data/area2_0530_2022_8bands_patches_A.tif', '/home/otbuser/all/data/area2_0530_2022_8bands_patches_B.tif']
    labels = ['/home/otbuser/all/data/area2_0530_2022_8bands_labels_A.tif', '/home/otbuser/all/data/area2_0530_2022_8bands_labels_B.tif']
    create_tfrecords(patches=patches[0:1], labels=labels[0:1], outdir=datapath+"train")
    create_tfrecords(patches=patches[1:], labels=labels[1:], outdir=datapath+"valid")
    # tf.compat.v1.disable_eager_execution()

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

    
    # tf.compat.v1.enable_eager_execution()
    train(datapath+"sandbox_model", batch_size, learning_rate, nb_epochs, ds_train, ds_valid, ds_test=None)
    tf.compat.v1.disable_eager_execution()


