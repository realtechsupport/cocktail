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
from helper import *

#----------------------------------------------------------
datapath = "/home/otbuser/all/data/"
input = "area2_0530_2022_8bands.tif"
'''
ds = gdal.Open(datapath + input)
n = ds.RasterCount
cols = ds.RasterYSize
rows = ds.RasterXSize
print("Input image bands, cols, rows: ", n, cols, rows)
'''
print("Running NDVI")
output = input.split(".tif")[0] + "_ndvi.png"
ndvi_superdove(datapath, input, output)
