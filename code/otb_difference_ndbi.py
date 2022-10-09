# COCKTAIL
# otb_difference_ndbi.py
# RTS, October 2022
#-------------------------------------------------------------------------------
# This script takes in two satellite assets
# It calculates differences of ndbi on satellite image data (either sentinel2 or landsat8)
# result threholded and superimposed on newer of the two satellite images
# ------------------------------------------------------------------------------
# The script assumes the input data is a zipped file of the image bands in one folder only
# The script sentinel2_getdata.py collects the data directly from ESA and produces that format
# If you collect the satellite data from a different source, you must clip the images to your ROI
# and create the zipped folder manually
# Zipped .tif band files must be in the collection directory
# 'area2_0726_2021_sentinel2.zip', 'area2_0727_2021_landsat8.zip'
#-------------------------------------------------------------------------------
# Landsat bands
# https://www.usgs.gov/faqs/what-are-band-designations-landsat-satellites
# https://earthexplorer.usgs.gov/
# Sentinel bands
# https://gisgeography.com/sentinel-2-bands-combinations/
# ------------------------------------------------------------------------------
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
# ------------------------------------------------------------------------------
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
datapath = '/home/marcbohlen/cocktail/data/'
inputsfile = datapath + 'settings.txt'
#------------------------------------------------------------------------------
def main():

	inputs = []
	bandseletion = 'na'
	enddate = 'na'
	uuid = 'na'

	print('\nYou can use this routine to create difference images of NDBI on satellite imagery of two different dates.')
	print('Supported satellite assets are: Sentinel2 or Landsat8 data - do not mix sources...')
	print('All inputs should have the same footprint - use otb_clip.py to clip to a selected ROI')
	print('\nThe datasets must reside in the collection directory.')
	print('At the prompt, enter the names of the datasets.')
	print('Example: area2_0726_2021_sentinel2.zip area2_0717_2017_sentinel2.zip')

	response = input("\nEnter your choices: ")
	try:
		elements = response.split(' ')
		satellitesource_a = elements[0]
		satellitesource_b = elements[1]
	except:
		if(len(elements) != 2):
			print('\nYou should specify two datasources.')
			exit()

	if(('.zip' in satellitesource_a) and ('.zip' in satellitesource_b)):
		print('\nSelected satellite assets: ', satellitesource_a, satellitesource_b)
		create_ndbi_difference_map(satellitesource_a, satellitesource_b)
	else:
		print("\Something went wrong...\n")
#------------------------------------------------------------------------------

def create_ndbi_difference_map (satellitesource_a, satellitesource_b):
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
		landsat8rasterpath = jdata['landsat8rasterpath']
		authfile = jdata['authfile']

		t2p = jdata['T2P']
		pdir = jdata['pdir']
		r_height = int(jdata['r_height'])
		r_width = int(jdata['r_width'])
		background = jdata['background']
		location = jdata['location']

	#---------------------------------------------------------------------------
	# step 1 - Preparation - copy the selected Sentinel or Landsat data to the raster folder and uncompress
	# --------------------------------------------------------------------------

	if(('landsat8' in satellitesource_a) and ('landsat8' in satellitesource_b)):
		satrasterpath = landsat8rasterpath
	else:
		satrasterpath = sentinelrasterpath

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
	#this depends on the naming convention of the zipped satelllite files
	#see sentinel2_getdata.py
	parts_a = satellitesource_a.split('_')
	if(len(parts_a) > 4):
		date = 2
		year = 3
	else:
		date = 1
		year = 2

	satname_a = parts_a[0] + '_' + parts_a[-1].split('.zip')[0]
	token_a = parts_a[year] + parts_a[date]

	parts_b = satellitesource_b.split('_')
	if(len(parts_b) > 4):
		date = 2
		year = 3
	else:
		date = 1
		year = 2

	satname_b = parts_b[0] + '_' + parts_b[-1].split('.zip')[0]
	token_b = parts_b[year] + parts_b[date]
	
	'''
	print('Partsa: ', parts_a) print('Partsb: ', parts_b)
	print('tokena: ', token_a) print('tokenb: ', token_b)
	'''

	ext = '.tif'
	c_ext = '.png'
	do_colormap = 'true'

	print('\nThis is the first satellite source and date: ', satname_a, token_a)
	print('\nThis is the second satellite source and date: ', satname_b, token_b)

	# ---------------------------------------------------------------------------------
	# step 2 - Perform NDBI on each image
	# --------------------------------------------------------------------------------

	print("\nNormalized Difference Built-up Index\n")
	if(('landsat8' in satellitesource_a) and ('landsat8' in satellitesource_b)):
		# operation: (B06 - B05) / (B06 + B05)
		nirband = 'B5'
		swirband = 'B6'
	else:
		#operation: (B11 − B8A) / ( B11 + B8A)
		nirband = 'B8A'
		swirband = 'B11'

	im1a = findband_roi(swirband, token_a, ext, satrasterpath)
	if(im1a == 'na'):
		im1a = findband(swirband, token_a, ext, satrasterpath)

	im2a = findband_roi(nirband, token_a, ext, satrasterpath)
	if(im2a == 'na'):
		im2a = findband(nirband, token_a, ext, satrasterpath)

	im1b = findband_roi(swirband, token_b, ext, satrasterpath)
	if(im1b == 'na'):
		im1b = findband(swirband, token_b, ext, satrasterpath)

	im2b = findband_roi(nirband, token_b, ext, satrasterpath)
	if(im2b == 'na'):
		im2b = findband(nirband, token_b, ext, satrasterpath)

	print('This is the swir band of the first asset: ', im1a)
	print('This is the nir band of the first asset: ', im2a)
	print('This is the swir band of the second asset: ', im1b)
	print('This is the nir band of the second asset: ', im2b)

	expression = "(im1b1 - im2b1) / (im1b1 + im2b1)"
	apptype = "BandMathX"
	app = otbApplication.Registry.CreateApplication(apptype)

	# operate on the first image
	print('\nOperating on first image...\n')
	im1 = im1a
	im2 = im2a
	satbandmathimage_a = satname_a + '_ndbi_' + token_a + ext
	#color_satbandmathimage = 'color_' + satname_a + '_' + type + '_' + token_a + ext
	app.SetParameterStringList("il", [satrasterpath + im1, satrasterpath + im2])
	app.SetParameterString("out", resultspath + satbandmathimage_a)
	app.SetParameterString("exp", expression)
	app.ExecuteAndWriteOutput()

	# operate on the second image
	print('\nOperating on second image...\n')
	im1 = im1b
	im2 = im2b
	satbandmathimage_b = satname_b + '_ndbi_' + token_b + ext
	#color_satbandmathimage = 'color_' + satname_b + '_' + type + '_' + token_b + ext
	app.SetParameterStringList("il", [satrasterpath + im1, satrasterpath + im2])
	app.SetParameterString("out", resultspath + satbandmathimage_b)
	app.SetParameterString("exp", expression)
	app.ExecuteAndWriteOutput()

	# ----------------------------------------------------------------------------------
	# step 3 - Difference between the two operations
	# ----------------------------------------------------------------------------------

	diff_satbandmathimage = 'diff_satbandmathimage' + ext
	im1 = satbandmathimage_a
	im2 = satbandmathimage_b

	expression = "(im1b1 - im2b1)"
	differenceoperation1 = True

	try:
		app.SetParameterStringList("il", [resultspath + im1, resultspath + im2])
		app.SetParameterString("out", resultspath + diff_satbandmathimage)
		app.SetParameterString("exp", expression)
		app.ExecuteAndWriteOutput()
	except:
		differenceoperation1 = False
		print('\nSomething might have gone wrong with the difference operation ...')

	if(differenceoperation1 == False):
		print('Clipping inputs to same dimensions...')
		command1 = "python3 otb_clip_ni.py " + im1 
		command2 = "python3 otb_clip_ni.py " + im2
		os.system(command1)
		os.system(command2)
		
		ext = '.tif'
		add = '_roi'
		im1 = satbandmathimage_a.split(ext)[0] + add + ext
		im2 = satbandmathimage_b.split(ext)[0] + add + ext

		print('new im1: ', im1)
		print('new im2: ', im2)
	
		try:
			app.SetParameterStringList("il", [resultspath + im1, resultspath + im2])
			app.SetParameterString("out", resultspath + diff_satbandmathimage)
			app.SetParameterString("exp", expression)
			app.ExecuteAndWriteOutput()
		except:
			print('\nSomething STILL wrong ... check the files..')
			exit()

	#-------------------------------------------------------------------------------
	# step 4 - Color mapping of difference image
	#-------------------------------------------------------------------------------

	if(do_colormap == 'true'):
		#get min and max for colormap
		img = gdal.Open(resultspath + diff_satbandmathimage)
		img_stats = img.GetRasterBand(1).GetStatistics(0,1)
		min_val = img_stats[0]
		max_val = img_stats[1]

		cmap = "hot"
		thres_diff_satbandmathimage = "thres_" + diff_satbandmathimage
		color_diff_satbandmathimage = "color_diffimage.png"
		color_thres_diff_satbandmathimage = "color_" + thres_diff_satbandmathimage.split('.tif')[0] + c_ext

		apptype = "ColorMapping"
		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterString("in", resultspath + diff_satbandmathimage)
		app.SetParameterString("method","continuous")
		app.SetParameterString("method.continuous.min", str(0))           #min_val
		app.SetParameterString("method.continuous.max", str(1))           #max_val
		app.SetParameterString("method.continuous.lut", cmap)
		app.SetParameterString("out", resultspath + color_diff_satbandmathimage)
		app.ExecuteAndWriteOutput()

	#--------------------------------------------------------------------------------
	# step 5 - Overlay on reference
	#--------------------------------------------------------------------------------

		#threshold the result with PIL
		#threshold at the middle (0 - 255) ... make this an input?
		threshold = 128
		temp = Image.open(resultspath + color_diff_satbandmathimage)
		temp = temp.point(lambda p: p > threshold and 255)
		temp.save(resultspath + color_thres_diff_satbandmathimage, "PNG")

		#Create overlay with B08 (NIR) of the NEWER image
		searchpath =  sentinelrasterpath
		
		#not necessary any more...
		'''
		if(differenceoperation1 == True):
			B08s = [band for band in os.listdir(searchpath) if(("B08" in band) and ("roi" in band))]
			if(len(B08s) == 0):
				B08s = [band for band in os.listdir(searchpath) if("B08" in band)]
		#not sure we still need this case..
		else:
			B08s = [band for band in os.listdir(searchpath) if(("B08" in band) and ("roi" not in band))]
			if(len(B08s) == 0):
				B08s = [band for band in os.listdir(searchpath) if("B08" in band)]
		'''
		
		B08s = [band for band in os.listdir(searchpath) if("B08" in band)]
		B08 = B08s[0]

		background = "B08.png"
		apptype = "DynamicConvert"
		app = otbApplication.Registry.CreateApplication(apptype)

		app.SetParameterString("in", searchpath + B08) 
		app.SetParameterString("type","linear")
		app.SetParameterString("out", resultspath + background)
		app.ExecuteAndWriteOutput()

		#Adjust images and blend via PIL
		finalimage = "ndbi_difference_overlay.png"
		red = Image.open(resultspath + color_thres_diff_satbandmathimage)
		red.convert('RGBA')
		red.putalpha(255)
		background = Image.open(resultspath + background)
		background.convert('RGBA')
		background.putalpha(255)

		red_new = red.resize(background.size)
		background_new = Image.new("RGBA", background.size)
		background_new.paste(background)
		#print(background_new.size, background_new.mode, background_new.info)

		blended = Image.blend(background_new, red_new, 0.75)
		blended.save(resultspath + finalimage, "PNG")
		print('\n\nDifference of selected band operation between first and second image in red, supperimposed on NIR of the newer image')
		print('\n')

		filelist = [inputsfile, resultspath + finalimage]

        #-------------------------------------------------------------------------------
        # step 6 -  Clean up the satellite data folder (sentinel2 or landsat8)
        #-------------------------------------------------------------------------------

		temp = [file for file in os.listdir(satrasterpath)]
		for file in temp:
			os.remove(satrasterpath + file)

	#-------------------------------------------------------------------------------
	# step 7 - File transfer
	#-------------------------------------------------------------------------------
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

#---------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
#---------------------------------------------------------------------------------
