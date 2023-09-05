# Testing data preparation for  ingestion into OTBTF deeplearning
# otbtf_helper.py
# helper file for data preparation and model training
# ---------------------------------------------------------------
# Patches selection, patches extraction
# Create train and test data sets (A and B)
# June 2023
#--------------------------------------------------------

import os, sys
import time
import numpy as np

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
import pickle

from tricks import *
from helper import *
from osgeo import gdal

#--------------------------------------------------------------------------------
def PolygonClassStatistics(apptype, datapath, input, vec, output):
	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterString("in", datapath + input)
	app.SetParameterString("vec", datapath + vec)
	app.SetParameterString("field", "class")
	app.SetParameterString("out", datapath + output)
	app.ExecuteAndWriteOutput()

#-------------------------------------------------------------------------------
def SampleSelection(apptype, datapath, input, vec, instats, output):
	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterString("in", datapath + input)
	app.SetParameterString("instats", datapath + instats)
	app.SetParameterString("vec", datapath + vec)
	app.SetParameterString("field", "class")
	app.SetParameterString("out", datapath + output)
	app.ExecuteAndWriteOutput()

#------------------------------------------------------------------------------
def PatchesExtraction(apptype, datapath, input, vec, out_patches, out_labels, patchsize):
	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterStringList("source1.il", [datapath + input])
	app.SetParameterString("source1.out", datapath + out_patches) 
	app.SetParameterInt("source1.patchsizex", patchsize)
	app.SetParameterInt("source1.patchsizey", patchsize)
	app.SetParameterString("vec", datapath + vec)
	app.SetParameterString("field", "class")
	app.SetParameterString("outlabels", datapath + out_labels)
	app.ExecuteAndWriteOutput()
	
#----------------------------------------------------------------------------
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

#----------------------------------------------------------------------------------
'''
# Train the deep learning model
otbcli_TensorflowModelTrain \
-training.source1.il Sentinel-2_B4328_10m_patches_A.tif \
-training.source1.patchsizex 16 \
-training.source1.patchsizey 16 \
-training.source1.placeholder "x" \
-training.source2.il Sentinel-2_B4328_10m_labels_A.tif \
-training.source2.patchsizex 1 \
-training.source2.patchsizey 1 \
-training.source2.placeholder "y" \
-model.dir model1 \
-training.targetnodes "optimizer" \
-validation.mode "class" \
-validation.source1.il Sentinel-2_B4328_10m_patches_B.tif \
-validation.source1.name "x" \
-validation.source2.il Sentinel-2_B4328_10m_labels_B.tif \
-validation.source2.name "prediction" \
-model.saveto model1/variables/variables

'''
#----------------------------------------------------------------------------
