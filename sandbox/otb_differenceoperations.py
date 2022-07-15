# COCKTAIL
# otb_differenceoperations.py
# RTS, July 2022
#-------------------------------------------------------------------------------
# takes in two satellite assets and a bandoperation
# calculates differences of band operations on satellite image data (either sentinel2 or landsat8)
# result threholded and superimposed on newer of the two satellite images
# ------------------------------------------------------------------------------
# get sentinel data via planet lab
# or directly from sentinel and convert .jp2 to geotif (.tif)

# Landsat bands
# https://www.usgs.gov/faqs/what-are-band-designations-landsat-satellites
# https://earthexplorer.usgs.gov/
# Sentinel bands
# https://gisgeography.com/sentinel-2-bands-combinations/
# ------------------------------------------------------------------------------

# Clip the images to the same area with otb_clip.py before you use this operation...

#-------------------------------------------------------------------------------
# Currently two operations supported: NDBI and NDVI

# Normalised Difference Built-up Index (NDBI)
# ndbi on Sentinel2:
# swir: B11
# nir: B08A
# operation: (B11 − B8A) / ( B11 + B8A)
# ndbi on Landsat8:
# swir1: B06
# nir: B05
# operation: (B06 - B05) / (B06 + B05)

# useful: https://github.com/CNES/ALCD/blob/master/L1C_band_composition.py

# Normalized difference Vegetation Index (NDVI)
# https://custom-scripts.sentinel-hub.com/custom-scripts/sentinel-2/ndvi/
# ndvi on Sentinel2
# nir: B8A
# red: 804
# operation: (B8A - B04) / (B8A + B04)
# ndvi on landsat8
# nir: B05
# red: B04
# operation: (B05 - B04) / (B05 + B04)
# ------------------------------------------------------------------------------
# General comments
# Input images must share same origin, resolution, size, projection.
# Clip the inputs with the same ROI file !
# Select / set the settings in the settings.txt file.
# Activate the OTB conda environment before you run this code
# conda activate OTB
# ------------------------------------------------------------------------

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

	inputs = []
	bandseletion = 'na'
	enddate = 'na'
	uuid = 'na'

	print('\nYou can use this routine to create difference images of band operations on satellite imagery of two different dates.')
	print('Supported satellite assets are: Sentinel2 or Landsat8 data - do not mix sources...')
	print('All inputs should have the same footprint - use otb_clip.py to clip to a selected ROI')
	print('\nThe compressed datasets, cliped to the same area, must reside in the collection directory.')
	print('Supported band operation options are: ndvi or nbdi')
	print('Enter the name of the datasets, followed by the band operation.')
	print('Example: area2_0726_2021_sentinel2.zip area2_0717_2017_sentinel2.zip ndbi')

	response = input("\nEnter your choices: ")
	try:
		elements = response.split(' ')
		satellitesource_a = elements[0]
		satellitesource_b = elements[1]
		type = elements[2]
	except:
		if(len(elements) != 3):
			print('\nYou should specify two datasources and the bandoperation.')
			ecit()

	if(('.zip' in satellitesource_a) and ('.zip' in satellitesource_b) and ((type == 'ndvi') or (type == 'ndbi'))):
		print('\nSelected satellite assets and band operation: ', satellitesource_a, satellitesource_b, type)
		create_change_map(satellitesource_a, satellitesource_b, type)
	else:
		print("\Only ndvi and ndbi supported. Try again...\n")
#------------------------------------------------------------------------------

def create_change_map (satellitesource_a, satellitesource_b, type):
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
		topsentinelrasterpath = jdata['topsentinelrasterpath']
		landsat8rasterpath = jdata['landsat8rasterpath']
		authfile = jdata['authfile']

		t2p = jdata['T2P']
		pdir = jdata['pdir']
		r_height = int(jdata['r_height'])
		r_width = int(jdata['r_width'])
		background = jdata['background']
		location = jdata['location']

	#---------------------------------------------------------------------------
	# step 1 - preparation - copy the selected Sentinel or Landsat data to the raster folder and uncompress

	if(('landsat8' in satellitesource_a) and ('landsat8' in satellitesource_b)):
		satrasterpath = landsat8rasterpath
	else:
		satrasterpath = topsentinelrasterpath

	#copy first dataset
	shutil.copy(collectionpath + satellitesource_a, satrasterpath)
	with zipfile.ZipFile(satrasterpath + satellitesource_a, 'r') as zip_ref:
		zip_ref.extractall(satrasterpath)

	#copy second dataset
	shutil.copy(collectionpath + satellitesource_b, satrasterpath)
	with zipfile.ZipFile(satrasterpath + satellitesource_b, 'r') as zip_ref:
		zip_ref.extractall(satrasterpath)

	print("Selected zipped files moved to vector directory and unzipped..")

	#_a and _b for the different timestamped images
	#_1 and _2 for the different band images
	parts_a = satellitesource_a.split('_')
	satname_a = parts_a[0] + '_' + parts_a[-1].split('.zip')[0]
	token_a = parts_a[2] + parts_a[1]

	parts_b = satellitesource_b.split('_')
	satname_b = parts_b[0] + '_' + parts_b[-1].split('.zip')[0]
	token_b = parts_b[2] + parts_b[1]

	ext = '.tif'
	c_ext = '.png'
	do_colormap = 'true'

	print('\nThis is the first satellite source and date: ', satname_a, token_a)
	print('\nThis is the second satellite source and date: ', satname_b, token_b)

	if(type == 'ndbi'):
		print("\nNormalized Difference Built-up Index\n")
		if(('landsat8' in satellitesource_a) and ('landsat8' in satellitesource_b)):
			# operation: (B06 - B05) / (B06 + B05)
			nirband = 'B5'
			swirband = 'B6'
		else:
			#operation: (B11 − B8A) / ( B11 + B8A)
			nirband = 'B8A'
			swirband = 'B11'

		if(satrasterpath == topsentinelrasterpath):
			satrasterpath = satrasterpath + "files/"

		print('here is the satrasterpath: ', satrasterpath)
		im1a = findband_roi(swirband, token_a, ext, satrasterpath)
		im2a = findband_roi(nirband, token_a, ext, satrasterpath)
		im1b = findband_roi(swirband, token_b, ext, satrasterpath)
		im2b = findband_roi(nirband, token_b, ext, satrasterpath)
		#cmap = 'relief'
		#cmap = 'hot'

		print('This is the swir band of the first asset: ', im1a)
		print('This is the nir band of the first asset: ', im2a)
		print('This is the swir band of the second asset: ', im1b)
		print('This is the nir band of the second asset: ', im2b)


	elif(type == 'ndvi'):
		print("\nNormalized Difference Vegetation Index\n")
		if(('landsat8' in satellitesource_a) and ('landsat8' in satellitesource_b)):
			# operation: (B05 - B04) / (B05 + B04)
			nirband = 'B5'
			redband = 'B4'
		else:
			# operation: (B8A - B04) / (B8A + B04)
			nirband = 'B8A'
			redband = 'B04'

		im1a = findband_roi(nirband, token_a, ext, satrasterpath)
		im2a = findband_roi(redband, token_a, ext, satrasterpath)
		im1b = findband_roi(nirband, token_b, ext, satrasterpath)
		im2b = findband_roi(redband, token_b, ext, satrasterpath)
		cmap = 'jet'

		print('This is the nir band of the first asset: ', im1a)
		print('This is the nir band of the first asset: ', im2a)
		print('This is the swir band of the second asset: ', im1b)
		print('This is the nir band of the second asset: ', im2b)

	#---------------------------------------------------------------------------

	expression = "(im1b1 - im2b1) / (im1b1 + im2b1)"
	apptype = "BandMathX"
	app = otbApplication.Registry.CreateApplication(apptype)

	# operate on the first image
	print('\noperating on first image...\n')
	im1 = im1a
	im2 = im2a
	satbandmathimage_a = satname_a + '_' + type +  '_' + token_a + ext
	color_satbandmathimage = 'color_' + satname_a + '_' + type + '_' + token_a + ext
	app.SetParameterStringList("il", [satrasterpath + im1, satrasterpath + im2])
	app.SetParameterString("out", resultspath + satbandmathimage_a)
	app.SetParameterString("exp", expression)
	app.ExecuteAndWriteOutput()

	# operate on the second image
	print('\noperating on second image...\n')
	im1 = im1b
	im2 = im2b
	satbandmathimage_b = satname_b + '_' + type +  '_' + token_b + ext
	color_satbandmathimage = 'color_' + satname_b + '_' + type + '_' + token_b + ext
	app.SetParameterStringList("il", [satrasterpath + im1, satrasterpath + im2])
	app.SetParameterString("out", resultspath + satbandmathimage_b)
	app.SetParameterString("exp", expression)
	app.ExecuteAndWriteOutput()

	# difference between the two band operations
	diff_satbandmathimage = 'diff_satbandmathimage' + ext
	im1 = satbandmathimage_a
	im2 = satbandmathimage_b


	# check for dimensions - if not same, clip ----------------------------------------
	#now: use the clipped imags (july14 currently in results folder...
	#im1 = 
	#im2 =

 
	#threshold = "-0.2"
	#expression = "((im1b1 - im2b1) < " + threshold + ") ? 0 : 1"
	expression = "(im1b1 - im2b1)"

	app.SetParameterStringList("il", [resultspath + im1, resultspath + im2])
	app.SetParameterString("out", resultspath + diff_satbandmathimage)
	app.SetParameterString("exp", expression)
	app.ExecuteAndWriteOutput()

	#this far OK !

#-------------------------------------------------------------------------------
# step 3 - color mapping
#-------------------------------------------------------------------------------
	if(do_colormap == 'true'):
		#get min and max for colormap
		img = gdal.Open(resultspath + diff_satbandmathimage)
		img_stats = img.GetRasterBand(1).GetStatistics(0,1)
		min_val = img_stats[0]
		max_val = img_stats[1]

		cmap = "hot"
		thres_diff_satbandmathimage = "thres_" + diff_satbandmathimage
		color_thres_diff_satbandmathimage = "color_" + thres_diff_satbandmathimage.split('.tif')[0] + c_ext

		print('\n\n')
		print(color_thres_diff_satbandmathimage)

		# swap color and then threshold ???  try....

		#first threshold
		apptype = "BandMathX"
		im1 = diff_satbandmathimage

		values = [float(min_val), float(max_val)]
		threshold = str(numpy.mean(values))

		print('\n\n\n')
		print(threshold)
		expression = "im1b1 > " + threshold + " ? 1 : 0"

		app.SetParameterStringList("il", [resultspath + im1])
		app.SetParameterString("out", resultspath + thres_diff_satbandmathimage)
		app.SetParameterString("exp", expression)
		app.ExecuteAndWriteOutput()


		#then color
		apptype = "ColorMapping"
		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterString("in", resultspath + thres_diff_satbandmathimage)
		app.SetParameterString("method","continuous")
		app.SetParameterString("method.continuous.min", str(0))           #min_val))
		app.SetParameterString("method.continuous.max", str(1))           #max_val))
		app.SetParameterString("method.continuous.lut", cmap)
		app.SetParameterString("out", resultspath + color_thres_diff_satbandmathimage)
		app.ExecuteAndWriteOutput()

		filelist = [inputsfile, resultspath + color_thres_diff_satbandmathimage]

#-------------------------------------------------------------------------------
# step 4 - file transfer
#-------------------------------------------------------------------------------
	'''
	if(t2p == "yes"):
		f = open(authfile, 'r')
		lines = f.readlines()
		username = lines[0].strip()
		password = lines[1].strip()
		f.close()

		conn = PyCloud(username, password, endpoint='nearest')
		conn.uploadfile(files=filelist, path=pdir)
		print('\n\nUploaded: ' , filelist)
		print('\n\n')
		'''
#---------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
#---------------------------------------------------------------------------------
