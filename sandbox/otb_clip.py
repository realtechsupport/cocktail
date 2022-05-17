# ORFEO Toolbox
# otb_clip.py
#--------------------------------------------------------------
# RTS, April 2022
# -------------------------------------------------------------

import sys, os
import json
import gdal
import otbApplication
import numpy
from PIL import Image as PILImage
from pcloud import PyCloud
from zipfile import ZipFile

from helper import *

# Local path and variables
datapath = '/home/blc/cocktail/data/'
inputsfile = datapath + 'settings.txt'
#------------------------------------------------------------------------------
def main():
	try:
        	f = open(inputsfile, 'r')
        	data = f.read()
        	jdata = json.loads(data)
        	f.close()
	except:
        	print('\n...data access error...\n')
	else:
		#print(jdata)
		rasterpath = jdata['rasterpath']
		vectorpath = jdata['vectorpath']
		resultspath = jdata['resultspath']
		collectionpath = jdata['collectionpath']
		sentinelrasterpath = jdata['sentinelrasterpath']
		authfile = jdata['authfile']

		t2p = jdata['T2P']
		pdir = jdata['pdir']
		r_height = int(jdata['r_height'])
		r_width = int(jdata['r_width'])
		background = jdata['background']
		location = jdata['location']

	#---------------------------------------------------------------------------
	# step 1 - clear the sentinel raster path
	filelist = [file for file in os.listdir(sentinelrasterpath)]
	for file in filelist:
		os.remove(sentinelrasterpath + file)

	# step 2 - preparation - copy the selected sentineldata to the raster folder and uncompress
	rastershapezipfile =  'area2_0717_2017_sentinel2.zip'
	shutil.copy(collectionpath + rastershapezipfile, rasterpath)
	with zipfile.ZipFile(rasterpath + rastershapezipfile, 'r') as zip_ref:
		zip_ref.extractall(rasterpath)

	print("Selected zipped files moved to vector directory and unzipped..")
	parts = rastershapezipfile.split('_')
	token = parts[2] + parts[1]
	ext = '.tif'

	# step 3 - move and unpack the shapefile to the ROI dir in the vectorpath
	roishapezipfile =  'area2_shape_crop.zip'
	roishape = roishapezipfile.split('.zip')[0] + '.shp'
	roipath = vectorpath + 'roi/'
	roipath_area2crop = roipath + roishapezipfile.split('.zip')[0] + '/'

	shutil.copy(collectionpath + roishapezipfile, roipath)
	with zipfile.ZipFile(roipath + roishapezipfile, 'r') as zip_ref:
		zip_ref.extractall(roipath)

	# step 4 - clip based on roi shapefile
	warp_options = gdal.WarpOptions(cutlineDSName = roipath_area2crop+roishape, cropToCutline = True)
	bandlist = [band for band in os.listdir(sentinelrasterpath) if band[-4:] == '.tif']

	for b in bandlist:
		b_new = b.split('.tif')[0] + '_roi' + ext
		print(b, b_new)
		ds = gdal.Warp(sentinelrasterpath + b_new, sentinelrasterpath + b, options = warp_options)
		ds = None

#-------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------
