# 92% of storage used … If you run out, you won't have enough storage to create, edit and upload files. Get 100 GB of storage for ₹130.00 ₹35.00/month for 3 months.
# Testing data preparation for  ingestion into OTBTF deeplearning
# otbf_main.py
# July 2023
#--------------------------------------------------------
# Reference
# https://forgemia.inra.fr/remi.cresson/otbtf/-/blob/c7a36485a31b86048bd3280f0731944d2dbdad47/test/tutorial_unittest.py
# https://otbtf.readthedocs.io/en/latest/app_sampling.html#patchesselection
# -------------------------------------------------------

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
scale_and_normalize_and_flatten(datapath, input, normalized_input, scale_min, scale_max)
print("\nImage normalized")
# ------------------------------------------------------------------------------
input = normalized_input                # use the normalized input !! 

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

#----------------------------------------------------------------------------

# call create model
# call model train
# call model test