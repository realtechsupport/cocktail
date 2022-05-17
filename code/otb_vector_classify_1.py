# COCKTAIL
# otb_vector_classify_1.py
# segmentation and zonal statistics
# RTS, Feb 2022

# sequence
# OTB_vector_classify1
# QGIS_join
# OTB__vector_classify2
# QGIS_render

# ----------------------------------------------------------------------------
import sys, os
import json
import gdal
import otbApplication
import numpy
import geopandas
from PIL import Image as PILImage
#------------------------------------------------------------------------------
print('\nVECTOR_CLASSIFY_1: Segmentation + Zonal Statistics\n')
#------------------------------------------------------------------------------
# Local path and variables
datapath = '/home/blc/cocktail/data/'
inputsfile = datapath + 'settings.txt'

#collect the variables from the settings file
try:
	f = open(inputsfile, 'r')
	data = f.read()
	jdata = json.loads(data)
	f.close()
except:
	print('\n...data access error...\n')
else:
	rasterimage = jdata['rasterimage']
	pointsfile = jdata['pointsfile']
	classifier = jdata['vector_classifier_ann']
	rasterpath = jdata['rasterpath']
	vectorpath = jdata['vectorpath']
	segmentationfile = jdata['segmentationfile']
	segmentation_stats = jdata['segmentation_stats']
	coord_info = jdata['coord_info']

#----------------------------------------------------------------------------
#only if you are working with a geojson input...
#geojsonfile = coord_info + '.geojson'
#shapefile = coord_info + '.shp'
#-----------------------------------------------------------------------------

if(classifier == 'ann'):
	print('\n\nPreparing pipeline for VECTOR classifier\n')
	#c1 shape from geojson
	#df = geopandas.read_file(datapath + geojsonfile)
	#df.to_file(vectorpath + shapefile)
	#print('created shapefile from geojson')

	#2 perform segmentation
	#https://www.orfeo-toolbox.org/CookBook/Applications/app_Segmentation.html
	app = otbApplication.Registry.CreateApplication("Segmentation")
	app.SetParameterString("in", rasterpath + rasterimage)
	app.SetParameterString("mode","vector")
	app.SetParameterString("mode.vector.out", vectorpath + segmentationfile)
	app.SetParameterString("filter","meanshift")
	app.ExecuteAndWriteOutput()

	#3 create statistics (zonalstatistics)
	app = otbApplication.Registry.CreateApplication("ZonalStatistics")
	app.SetParameterString("in", rasterpath + rasterimage)
	app.SetParameterString("inzone.vector.in", vectorpath + segmentationfile)
	app.SetParameterString("out.vector.filename", vectorpath + segmentation_stats)
	app.ExecuteAndWriteOutput()

	print('\n\nSegmentation and ZonalStatistics complete \n')
	#NEXT STEP: QGIS join
#---------------------------------------------------------------------------------
