# GISlogics - streamlit_helper.py
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
from PIL import Image
from tricks import *

from osgeo import gdal

import streamlit as st

datapath =  "/home/otbuser/all/data/"
imagepath = "/home/otbuser/all/data/images/"
videopath = "/home/otbuser/all/data/videos/"
modelpath =  "/home/otbuser/all/data/models/"

#---------------------------------------------------------
def do_classification(inputimage, imagepath, outputimage, model, datapath, modelpath):
        #print(datapath)
        #print(modelpath)
        apptype = "ImageClassifier"
        app = otbApplication.Registry.CreateApplication(apptype)
        app.SetParameterString("in", imagepath + inputimage)
        app.SetParameterString("model", modelpath + model)
        #app.SetParameterString("confmap", resultspath + confidencemap)
        app.SetParameterString("out", datapath + outputimage)
        app.ExecuteAndWriteOutput()

#------------------------------------------------------------
def do_vector_classification(inputimage, imagepath, outputimage, model, datapath, modelpath):
	# perform segmentation
	apptype = "Segmentation"
	segmentationfile =  "segmentation_vector.shp"
	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterString("in", imagepath + inputimage)
	app.SetParameterString("mode","vector")
	app.SetParameterString("mode.vector.out", datapath + segmentationfile)
	app.SetParameterString("filter","meanshift")
	app.ExecuteAndWriteOutput()
	print("Segmentation complete")

	# create statistics (zonalstatistics)
	apptype = "ZonalStatistics"
	segmentation_stats =  "segmentation_vector_stats.shp"
	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterString("in", imagepath + inputimage)
	app.SetParameterString("inzone.vector.in", datapath + segmentationfile)
	app.SetParameterString("out.vector.filename", datapath + segmentation_stats)
	app.ExecuteAndWriteOutput()
	print("Zonal stats complere")



	'''
        apptype = "ImageClassifier"
        app = otbApplication.Registry.CreateApplication(apptype)
        app.SetParameterString("in", imagepath + inputimage)
        app.SetParameterString("model", modelpath + model)
        #app.SetParameterString("confmap", resultspath + confidencemap)
        app.SetParameterString("out", datapath + outputimage)
        app.ExecuteAndWriteOutput()
	'''


#------------------------------------------------------------
def do_colormap(outputimage, c_outputimage, datapath, colormap):
	apptype = "ColorMapping"
	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterString("in", datapath + outputimage) 

	#img = gdal.Open(datapath + outputimage)
	#img_stats = img.GetRasterBand(1).GetStatistics(0,1)
	#min_val = img_stats[0]
	#max_val = img_stats[1]

	if(".txt" in colormap):
		print("applying custom colormap: ", colormap)
		app.SetParameterString("method", "custom")
		app.SetParameterString("method.custom.lut", datapath + colormap)
	else:
		app.SetParameterString("method", "continuous")
		#app.SetParameterString("method.continuous.min", str(min_val))           #min_val
		#app.SetParameterString("method.continuous.max", str(max_val))           #max_val
		app.SetParameterString("method.continuous.lut", colormap)

	app.SetParameterString("out", datapath + c_outputimage)
	app.ExecuteAndWriteOutput()

#------------------------------------------------------------

