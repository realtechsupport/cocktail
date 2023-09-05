# otbtf import tests
# test otb python api
# test gdal calls
# june 2023
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

from tricks import *

from osgeo import gdal

# set your data path accordingly
datapath = "/home/otbuser/all/data/"
print("\n\nImported otbtf ulitities...")
print("datapath: ", datapath)

# make sure you have uploaded this asset to the data directory
input = "area2_0530_2022_8bands.tif"
output = input.split(".tif")[0] + "_scaled.tif"
output2 = input.split(".tif")[0] + "_smoothed.tif"

# test otb access -----------------------------------------------------------
# print (str( otbApplication.Registry.GetAvailableApplications()))
# print("\n\n")

# test otb functionality ----------------------------------------------------
app = otbApplication.Registry.CreateApplication("Smoothing")
print (app.GetParametersKeys())

app.SetParameterString("in", datapath + input)
app.SetParameterString("type", 'gaussian')
app.SetParameterString("out", datapath + output2)
app.ExecuteAndWriteOutput()

# normalize the data values with GDAL ---------------------------------------- 
scale = '-scale 0 65535 0 1'
options_list = ['-ot Float32','-of GTIFF', scale] 
options_string = " ".join(options_list)
ds = gdal.Translate(datapath + output, datapath + input, options=options_string)
ds = None

#PolygonClassStatistics--------------------------------------------------------
out = 'vec_stats.xml'
poly = otbApplication.Registry.CreateApplication("PolygonClassStatistics")
inp = 'area2_0123_2023_raster_classification_13.shp'
poly.SetParameterString("vec", datapath + inp)
poly.SetParameterString("field", "class")
poly.SetParameterString("in", datapath + output)
poly.SetParameterString("out", datapath + out)
poly.ExecuteAndWriteOutput()
#------------------------------------------------------------------------------


