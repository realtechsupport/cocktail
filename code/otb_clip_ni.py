# COCKTAIL
# otb_clip_ni.py
# RTS, Oct 2022
#-------------------------------------------------------------------------------
# Clip a a single raster band image with an ROI file defined in the settings.
# ------------------------------------------------------------------------------
# Clip shape file must be contained within the (larger) input raster band images.
# Works on Landsat, Sentinel and Planet Labs assets.
# Check the collection directory for the zipped band images file
#
# Check the roi directory (in vectorfiles/roi) for the zipped ROI clip file
# Check the settings.txt file for the name of the roi file.
#-------------------------------------------------------------------------------
# Usage: python3 otb_clip_ni.py raster_to_clip.tif
# Call from otb_difference_ndbi.py
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
	for arg in sys.argv[1:]:
		print ("\nOTB_clip_ni ...this the selected input: ", arg)
		rasterfile = arg.strip()

	clip_source(rasterfile)
#------------------------------------------------------------------------------
def clip_source(rasterfile):
	#step 1 - get settings
	try:
        	f = open(inputsfile, 'r')
        	data = f.read()
        	jdata = json.loads(data)
        	f.close()
	except:
        	print('\n...data access error...\n')
	else:
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
	print('\nPerforming the clip operation on: ', rasterfile)
	ext = '.tif'
	warp_options = gdal.WarpOptions(cutlineDSName = roipath + roishape, cropToCutline = True)
	rasterfile_new = rasterfile.split(ext)[0] + '_roi' + ext
	ds = gdal.Warp(resultspath + rasterfile_new, resultspath + rasterfile,  options = warp_options)
	ds = None
	print('\nClipped raster input: ', rasterfile_new)
	print('saved to: ', resultspath)

#------------------------------------------------------------------------------
if __name__ == "__main__":
    main()

#-------------------------------------------------------------------------------
