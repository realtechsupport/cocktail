# COCKTAIL
# otb_clip.py
# RTS, July 2022
#-------------------------------------------------------------------------------
# Clip a collection of raster band images with an ROI file defined in the settings.
# ------------------------------------------------------------------------------
# Clip shape file must be contained within the (larger) input raster band images.
# Works on Landsat, Sentinel and Planet Labs assets.
# Check the collection directory for the zipped band images file
# Check the roi directory (in vectorfiles/roi) for the zipped ROI clip file
# Check the settings.txt file for the name of the roi file.
#-------------------------------------------------------------------------------
# Usage: python3 otb_clip.py (then follow the prompts)
#-------------------------------------------------------------------------------
import sys, os
import json
import gdal
import otbApplication
import numpy
from PIL import Image as PILImage
from zipfile import ZipFile

from helper import *

# Local path and variables
datapath = '/home/blc/cocktail/data/'
inputsfile = datapath + 'settings.txt'
#------------------------------------------------------------------------------
def main():

	inputs = []
	rastershapezipfile = 'na'

	print('\nUse this routine to clip existing satellite bands to an ROI specified in settings.txt')
	response = input("\nEnter the name of the zipped rasterbands file (such as area2_0726_2021_sentinel2.zip): ")
	try:
		rastershapezipfile = response.strip()
	except:
		if(len(elements) != 1):
			print('\nYou need the specify the input rasterfile')
			exit()

	if('.zip' in rastershapezipfile):
		print('Selected raster input: ', rastershapezipfile)
		clip_source(rastershapezipfile)
	else:
		print("\Something went wrong ... Try again...\n")

#------------------------------------------------------------------------------
def clip_source(rastershapezipfile):

	#step 1 - get settings
	try:
        	f = open(inputsfile, 'r')
        	data = f.read()
        	jdata = json.loads(data)
        	f.close()
	except:
        	print('\n...data access error...\n')
	else:
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
		roi = jdata['roi']
		roipath = jdata['roipath']


	print('Applying this ROI file: ', roi)

	# step 2 - preparation - copy the selected sentineldata to the raster folder and uncompress
	try:
		shutil.copy(collectionpath + rastershapezipfile, rasterpath)
		with zipfile.ZipFile(rasterpath + rastershapezipfile, 'r') as zip_ref:
			zip_ref.extractall(rasterpath)
	except:
		print('\nCould not  find the specified raster file - check the collection directory')
		exit()

	parts = rastershapezipfile.split('_')
	token = parts[2] + parts[1]
	ext = '.tif'

	# step 3 - move and unpack the shapefile to the ROI dir in the vectorpath
	roishape = roi.split('.zip')[0] + '.shp'

	try:
		shutil.copy(collectionpath + roi, roipath)
		with zipfile.ZipFile(roipath + roi, 'r') as zip_ref:
			zip_ref.extractall(roipath)
	except:
		print('\nCould not find the specified ROI reference file - check the roi directory or the settings file')
		exit()

	# step 4 - clip based on roi shapefile
	print('\nPerforming the clip operation...\n')
	warp_options = gdal.WarpOptions(cutlineDSName = roipath + roishape, cropToCutline = True)
	bandlist = [band for band in os.listdir(sentinelrasterpath) if band[-4:] == '.tif']

	for b in bandlist:
		if('_roi' in b):
			pass
		else:
			b_new = b.split('.tif')[0] + '_roi' + ext
			print(b, b_new)
			ds = gdal.Warp(sentinelrasterpath + b_new, sentinelrasterpath + b, options = warp_options)
			ds = None

#-------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#-------------------------------------------------------------------------------
