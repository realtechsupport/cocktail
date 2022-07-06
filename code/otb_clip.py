# COCKTAIL
# otb_clip.py
# RTS, July 2022
#-------------------------------------------------------------------------------
# clip a collection of raster band images based on a specified ROI files(both zipped)
# ------------------------------------------------------------------------------
# Clip shape file must be contained within the (larger) input raster band images.
# Works on Landsat, Sentinel and Planet Labs assets.
# Check the collection directory for the zipped band images file
# Check the roi directory (in vectorfiles/roi) for the zipped ROI clip file
#-------------------------------------------------------------------------------
# Usage: python3 otb_clip.py (then follow the prompts)
#-------------------------------------------------------------------------------
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

	#rastershapezipfile =  'area2_0726_2021_sentinel2.zip'
	#roishapezipfile =  'area2_shape_crop.zip'
	inputs = []
	rastershapezipfile = 'na'
	roishapezipfile = 'na'

	print('\nUse this routine to clip existing satellite image to a specific ROI')
	print('Enter first the input rasterfile and then the desired ROI file')
	print('Example: area2_0726_2021_sentinel2.zip area2_shape_crop.zip')
	response = input("\nEnter your choices: ")
	try:
		elements = response.split(' ')
		rastershapezipfile = elements[0]
		roishapezipfile = elements[1]
	except:
		if(len(elements) != 2):
			print('\nYou need the specify both the input rasterfile and the ROI file')
			exit()

	if(('.zip' in rastershapezipfile) and ('.zip' in roishapezipfile )):
		print('Selected raster input and reference ROI: ', rastershapezipfile, roishapezipfile)
		clip_source(rastershapezipfile, roishapezipfile)
	else:
		print("\Something went wrong ... Try again...\n")

#------------------------------------------------------------------------------
def clip_source(rastershapezipfile, roishapezipfile):

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
	roishape = roishapezipfile.split('.zip')[0] + '.shp'
	roipath = vectorpath + 'roi/'
	roipath_area2crop = roipath + roishapezipfile.split('.zip')[0] + '/'

	try:
		shutil.copy(collectionpath + roishapezipfile, roipath)
		with zipfile.ZipFile(roipath + roishapezipfile, 'r') as zip_ref:
			zip_ref.extractall(roipath)
	except:
		print('\nCould not find the specified ROI reference file - check the roi directory')
		exit()

	# step 4 - clip based on roi shapefile
	print('\nPerforming the clipping operation...\n')
	warp_options = gdal.WarpOptions(cutlineDSName = roipath_area2crop+roishape, cropToCutline = True)
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
