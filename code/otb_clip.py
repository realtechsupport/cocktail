# COCKTAIL
# otb_clip.py
# RTS, July 2022
#-------------------------------------------------------------------------------
# Clip a a singel or a collection of raster band images with an ROI file defined in the settings.
# ------------------------------------------------------------------------------
# Clip shape file must be contained within the (larger) input raster band images.
# Works on Landsat, Sentinel and Planet Labs assets.
# Check the collection directory for the zipped band images file
# If you want to clip a single raster image, follow to prompt to indicate name and path..
#
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
datapath = '/home/marcbohlen/cocktail/data/'
inputsfile = datapath + 'settings.txt'

#------------------------------------------------------------------------------
def main():

	inputs = []
	rastershapezipfile = 'na'
	selection = 'na'

	print('\nUse this routine to clip existing satellite bands to an ROI specified in settings.txt')
	response = input("\nEnter the name of the single (area2_sentinel_ndbi.tif) followed by space and the fully qualified path to the directory OR zipped rasterbands (such as area2_0726_2021_sentinel2.zip): ")

	try:
		selection = response.strip()
		inputs = selection.split(' ')
	except:
		if(len(inputs) == 0):
			print('\nYou need the specify the input rasterfile')
			exit()

	print('Selected input: ', inputs)



	if('.zip' in inputs[0]):
		rastershapezipfile = inputs[0]
		clip_source_multiple(rastershapezipfile)
	else:
		rasterfile = inputs[0]
		path2directory = inputs[1]
		firstchar = path2directory[0]
		lastchar = path2directory[-1]
		if(firstchar != '/'):
			path2directory = '/' + path2directory
		if(lastchar != '/'):
			path2directory = path2directory + '/'

		clip_source(rasterfile, path2directory)

#------------------------------------------------------------------------------
def clip_source(rasterfile, path2directory):
	#step 1 - get settings
	try:
        	f = open(inputsfile, 'r')
        	data = f.read()
        	jdata = json.loads(data)
        	f.close()
	except:
        	print('\n...data access error...\n')
	else:
		#vectorpath = jdata['vectorpath']
		resultspath = jdata['resultspath']
		collectionpath = jdata['collectionpath']
		location = jdata['location']
		roi = jdata['roi']
		roipath = jdata['roipath']

	# step 2 - move and unpack the shapefile to the ROI dir in the vectorpath
	roishape = roi.split('.zip')[0] + '.shp'

	try:
		shutil.copy(collectionpath + roi, roipath)
		with zipfile.ZipFile(roipath + roi, 'r') as zip_ref:
			zip_ref.extractall(roipath)
	except:
		print('\nCould not find the specified ROI reference file - check the roi directory or the settings file')
		exit()

	# step 3 - clip based on roi shapefile
	print('\nPerforming the clip operation...\n')
	ext = '.tif'
	warp_options = gdal.WarpOptions(cutlineDSName = roipath + roishape, cropToCutline = True)
	rasterfile_new = rasterfile.split('.tif')[0] + '_roi' + ext
	ds = gdal.Warp(resultspath + rasterfile_new, path2directory + rasterfile,  options = warp_options)
	ds = None
	print('\nClipped raster input: ', rasterfile_new)
	print('saved to: ', resultspath)

#------------------------------------------------------------------------------
def clip_source_multiple(rastershapezipfile):

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
	print('\nClipped roi files saved to: ', sentinelrasterpath)
#-------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#-------------------------------------------------------------------------------
