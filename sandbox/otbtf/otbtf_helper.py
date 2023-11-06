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



def LabelImageSampleSelection():
	app = otbApplication.Registry.CreateApplication(LabelImageSampleSelection)
	app.SetParameterString("in", datapath + input)
	app.SetParameterString("instats", datapath + instats)
	app.SetParameterString("vec", datapath + vec)
	app.SetParameterString("field", "class")
	app.SetParameterString("out", datapath + output)
	app.ExecuteAndWriteOutput()
#------------------------------------------------------------------------------

def PatchesExtraction(apptype, datapath, input, vec, out_patches, out_labels, patchsize):
	os.environ["OTB_TF_NSOURCES"] = "2"
	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterStringList("source1.il", [datapath + input])
	app.SetParameterInt("source1.patchsizex", patchsize)
	app.SetParameterInt("source1.patchsizey", patchsize)
	# app.SetParameterInt("source1.nodata", 0)
	# app.SetParameterStringList("source2.il", [datapath + input])
	# app.SetParameterInt("source2.patchsizex", patchsize)
	# app.SetParameterInt("source2.patchsizey", patchsize)
	# app.SetParameterInt("source2.nodata", 0)
	app.SetParameterStringList("source2.il", [datapath + input])
	app.SetParameterInt("source2.patchsizex", patchsize)
	app.SetParameterInt("source2.patchsizey", patchsize)
	# app.placeholder
	# app.SetParameterInt("source3.patchsizez", 1)
	# app.SetParameterInt("source2.nodata", 0)
	# app.SetParameterString("source1.out", datapath + "discard" + out_patches)
	app.SetParameterString("source1.out", datapath + out_patches)
	app.SetParameterString("source2.out", datapath + out_labels)
	# app.SetParameterString("source2.out", "uint8")
	# app.SetParameterString("outlabels", datapath + out_labels)	# if making it source2.out then it's creating (patchsize x patchsize x 8)
	# app.SetParameter

	app.SetParameterString("vec", datapath + vec)
	app.SetParameterString("field", "class")
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
        est