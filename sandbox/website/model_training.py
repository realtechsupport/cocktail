import os, sys
import time
import numpy as np
import pickle
import tensorflow as tf

import otbtf
import otbApplication

import otbtf.tfrecords
import otbtf.utils

from osgeo import gdal
from otbtf import DatasetFromPatchesImages
from otbtf.model import ModelBase
from otbtf import TFRecords
from otbtf.examples.tensorflow_v2x.fcnn import fcnn_model
from otbtf.examples.tensorflow_v2x.fcnn import helper

from tricks import *
from helper import *
from osgeo import gdal

datapath = "/home/otbuser/all/data/"
print("datapath: ", datapath)

# Ensure that the input image is normalized before proceeding with the next steps
#input = "area2_0530_2022_8bands_norm.tif"
input = 'area2_0530_2022_8bands.tif'
output = 'area2_0530_2022_8bands_norm.tif'
scale_min = 0
scale_max = 65535

out_patches_A = input.split('.')[0] + "_patches_A.tif"
out_labels_A = input.split('.')[0] + "_labels_A.tif"

out_patches_B = input.split('.')[0] + "_patches_B.tif"
out_labels_B = input.split('.')[0] + "_labels_B.tif"

def dataprep():
    # ------------------------------------------------------------------------------

    scale_and_normalize(datapath, input, output, scale_min, scale_max)

    apptype = "PolygonClassStatistics"
    app = otbApplication.Registry.CreateApplication(apptype)
    print(apptype)
    print("\n\n")
    print (app.GetParametersKeys())

    app.SetParameterString("in", datapath + input)
    app.SetParameterString("vec", datapath + "area2_0123_2023_raster_classification_13.shp")
    app.SetParameterString("field", "class")
    app.SetParameterString("out", datapath + "area2_0123_2023_raster_classification_13_vecstats.xml")
    app.ExecuteAndWriteOutput()

    apptype = "SampleSelection"
    app = otbApplication.Registry.CreateApplication(apptype)
    print(apptype)
    print("\n\n")
    print (app.GetParametersKeys())

    # A set
    app.SetParameterString("in", datapath + input)
    app.SetParameterString("instats", datapath + "area2_0123_2023_raster_classification_13_vecstats.xml")
    app.SetParameterString("vec", datapath + "area2_0123_2023_raster_classification_13.shp")
    app.SetParameterString("field", "class")
    app.SetParameterString("out", datapath + "area2_0123_2023_raster_classification_13_points_A.shp")
    app.ExecuteAndWriteOutput()

    # B set
    app.SetParameterString("in", datapath + input)
    app.SetParameterString("instats", datapath + "area2_0123_2023_raster_classification_13_vecstats.xml")
    app.SetParameterString("vec", datapath + "area2_0123_2023_raster_classification_13.shp")
    app.SetParameterString("field", "class")
    app.SetParameterString("out", datapath + "area2_0123_2023_raster_classification_13_points_B.shp")
    app.ExecuteAndWriteOutput()
    #---------------------------------------------------------------------------
    apptype = "PatchesExtraction"
    app = otbApplication.Registry.CreateApplication(apptype)
    print(apptype)
    print("\n\n")
    print (app.GetParametersKeys())

    patchsize = 64   #16
    # A set
    app.SetParameterStringList("source1.il", [datapath + input])
    app.SetParameterString("source1.out", datapath + out_patches_A) 
    app.SetParameterInt("source1.patchsizex", patchsize)
    app.SetParameterInt("source1.patchsizey", patchsize)
    app.SetParameterString("vec", datapath + "area2_0123_2023_raster_classification_13_points_A.shp")
    app.SetParameterString("field", "class")
    app.SetParameterString("outlabels", datapath + out_labels_A)
    app.ExecuteAndWriteOutput()

    # B set
    app.SetParameterStringList("source1.il", [datapath + input])
    app.SetParameterString("source1.out", datapath + out_patches_B) 
    app.SetParameterInt("source1.patchsizex", patchsize)
    app.SetParameterInt("source1.patchsizey", patchsize)
    app.SetParameterString("vec", datapath + "area2_0123_2023_raster_classification_13_points_B.shp")
    app.SetParameterString("field", "class")
    app.SetParameterString("outlabels", datapath + out_labels_B)
    app.ExecuteAndWriteOutput()


#---Model-------------------------------------------------------------------------------------------------------------------
class Model2(tf.keras.Model):
    def __init__(self, nclasses):
        super(Model2, self).__init__()
        self.nclasses = nclasses
        self.conv1 = tf.keras.layers.Conv2D(16, (5, 5), padding="valid", activation=tf.nn.relu)
        self.pool1 = tf.keras.layers.MaxPooling2D(pool_size=(2, 2), strides=2)
        self.conv2 = tf.keras.layers.Conv2D(16, (3, 3), padding="valid", activation=tf.nn.relu)
        self.pool2 = tf.keras.layers.MaxPooling2D(pool_size=(2, 2), strides=2)
        self.conv3 = tf.keras.layers.Conv2D(32, (2, 2), padding="valid", activation=tf.nn.relu)
        self.flatten = tf.keras.layers.Flatten()
        self.estimated = tf.keras.layers.Dense(128, activation=tf.nn.relu)
        self.estimated2 = tf.keras.layers.Dense(nclasses, activation=None)

    def call(self, inputs):
        x = self.conv1(inputs)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.pool2(x)
        x = self.conv3(x)
        features = self.flatten(x)
        estimated = self.estimated(features)
        estimated2 = self.estimated2(estimated)
        estimated_label = tf.argmax(estimated2, axis=1, name="prediction")
        return (estimated2, estimated_label)

#--Train the Model--------------------------------------------
def train():
    
    #-----------------------
    app = otbApplication.Registry.CreateApplication("TensorflowModelTrain")

    # Set the input parameters
    app.SetParameterStringList("training.source1.il", [datapath + out_patches_A])
    app.SetParameterInt("training.source1.patchsizex", 16)
    app.SetParameterInt("training.source1.patchsizey", 16)
    app.SetParameterString("training.source1.placeholder", "x")

    app.SetParameterStringList("training.source2.il", [datapath + out_labels_A])
    app.SetParameterInt("training.source2.patchsizex", 1)
    app.SetParameterInt("training.source2.patchsizey", 1)
    app.SetParameterString("training.source2.placeholder", "prediction")

    app.SetParameterString("model.dir", "/home/otbuser/all/data/model2.pb/")
    app.SetParameterStringList("training.targetnodes", ["optimizer"])
    app.SetParameterString("validation.mode", "class")

    app.SetParameterStringList("validation.source1.il", [datapath + out_patches_B])
    app.SetParameterString("validation.source1.name", "x")

    app.SetParameterStringList("validation.source2.il", [datapath + out_labels_B])
    app.SetParameterString("validation.source2.name", "prediction")

    app.SetParameterString("model.saveto", "/home/otbuser/all/data/")

    # Execute the application
    app.Execute()


def trained_model():
    #-----------------
    # Create the OTBTF application
    app = otbApplication.Registry.CreateApplication("TensorflowModelServe")

    # Set the input parameters
    app.SetParameterStringList("source1.il", [datapath + output])
    app.SetParameterInt("source1.rfieldx", 16)
    app.SetParameterInt("source1.rfieldy", 16)
    app.SetParameterString("source1.placeholder", "x")

    app.SetParameterString("model.dir", "/home/otbuser/all/data/model2.pb/")
    app.SetParameterString("output.names", "prediction")
    app.SetParameterString("out", "classif_model2.tif?&box=4000:4000:1000:1000")

    # Execute the application
    app.ExecuteAndWriteOutput()


#---Main function-------------------------------
if __name__ == "__main__":
    # dataprep
    dataprep()
    # Define inputs and outputs
    inputs = tf.keras.Input(shape=[64, 64, 8], name="x")
    labels = tf.keras.Input(shape=[64, 64, 1], name="prediction", dtype=tf.int32)
    nclasses = 20
    lr = 0.002

    # Create the model
    model = Model2(nclasses)

    # Output
    y_estimated, y_label = model(inputs)

    # Loss function
    cost = tf.losses.sparse_softmax_cross_entropy(tf.reshape(labels, [-1, 1]),
                                                     tf.reshape(y_estimated, [-1, nclasses]))
    optimizer = tf.keras.optimizers.Adam(learning_rate=lr)

    # Save the model
    modelname = "model2.pb"

    #model.save(datapath+modelname, save_format='tf')
    # model.save(modelname, save_format='tf')
    tf.saved_model.save(model, datapath+modelname)

    #training
    train()
    trained_model()
