# ORFEO Toolbox 
# classifier training and image classification
# install on Ubuntu 18 LTS with conda (conda-packages1.sh and environmentv1.yml.)
# RTS, Nov 2021
# OTB_part1

#sequence
# OTB_part1
# QGIS_join
# OTB_part2
# QGIS_render
# -------------------------------------------------------------
import sys, os
import json
import gdal
import otbApplication
import numpy 
import geopandas
from PIL import Image as PILImage
#------------------------------------------------------------------------------
# Local path and variables
datapath = '/home/marcbohlen/data/'
inputsfile = datapath + 'settings.txt'
#collect the variables
try:
	f = open(inputsfile, 'r')
	data = f.read()
	jdata = json.loads(data)
	f.close()
except:
	print('\n...data access error...\n')
else:
	print('\nHere are the settings parameters:\n\n')
	print(jdata)
	rasterimage = jdata['rasterimage']
	pointsfile = jdata['pointsfile']
	classifier_type = jdata['vector_classifier']
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

if(classifier_type == 'ann'):
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
