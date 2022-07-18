# COCKTAIL
# otb_ndbi.py
# RTS, July 2022
#-------------------------------------------------------------------------------
# ndbi on sentinel and landsat image data
# ------------------------------------------------------------------------------
# get sentinel data via planet lab
# or directly from sentinel and convert .jp2 to geotif (.tif)

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

# ------------------------------------------------------------------------------
# General comments
# Activate the OTB conda environment before you run this code
# conda activate OTB
# # Zipped .tif band files should be in the collection directory
# 'area2_0726_2021_sentinel2.zip', 'area2_0727_2021_landsat8.zip'
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

	print('\nYou can use this routine to perform NDBI on Sentinel2 or Landsat8 data')
	print('\nThe compressed datasets must reside in the collection directory.')
	print('Enter the name of the dataset.')
	print('Example: area2_0726_2021_sentinel2.zip')

	response = input("\nEnter your choices: ")
	try:
		elements = response.split(' ')
		satellitesource = response.strip()
	except:
		if(len(elements) != 1):
			print('\nYou need the specify the datasource.')
			exit()

	if('.zip' in satellitesource):
		print('\n Getting the selected asset: ', satellitesource)
		create_ndbi_map(satellitesource)
	else:
		print("\nSomething went wrong...Try again...\n")
#------------------------------------------------------------------------------

def create_ndbi_map (satellitesource):
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
		#r_height = int(jdata['r_height'])
		#r_width = int(jdata['r_width'])
		#background = jdata['background']
		#location = jdata['location']

	#---------------------------------------------------------------------------
	# step 1 - preparation - copy the selected Sentinel or Landsat data to the raster folder and uncompress
	# --------------------------------------------------------------------------

	if('landsat8' in satellitesource):
		satrasterpath = landsat8rasterpath
	else:
		satrasterpath = topsentinelrasterpath

	shutil.copy(collectionpath + satellitesource, satrasterpath)
	with zipfile.ZipFile(satrasterpath + satellitesource, 'r') as zip_ref:
		zip_ref.extractall(satrasterpath)

	print("Selected zipped files moved to vector directory and unzipped..")

	parts = satellitesource.split('_')
	satname = parts[0] + '_' + parts[-1].split('.zip')[0]
	token = parts[2] + parts[1]
	ext = '.tif'
	c_ext = '.png'
	do_colormap = 'true'

	print('\nThis is the satellite source and date: ', satname, token)

	#---------------------------------------------------------------------------
	# step 2  - ndbi operation
	#---------------------------------------------------------------------------

	print("\nNormalized Difference Built-up Index\n")
	# select the appropriate bands
	if('landsat8' in satellitesource):
		nirband = 'B5'
		swirband = 'B6'
	else:
		nirband = 'B8A'
		swirband = 'B11'

	if(satrasterpath == topsentinelrasterpath):
		satrasterpath = satrasterpath + "files/"
	print('Here is the satrasterpath: ', satrasterpath)

	im1 = findband_roi(swirband, token, ext, satrasterpath)
	im2 = findband_roi(nirband, token, ext, satrasterpath)
	cmap = 'relief'

	print('This is the swir band: ', im1)
	print('This is the nir band: ', im2)
	print('\n\n')

	apptype = "BandMathX"
	satbandmathimage = satname + '_ndbi_' + token + ext
	color_satbandmathimage = 'color_' + satname + '_ndbi_' + token + c_ext

	app = otbApplication.Registry.CreateApplication(apptype)
	expression = "(im1b1 - im2b1) / (im1b1 + im2b1)"
	app.SetParameterStringList("il", [satrasterpath + im1, satrasterpath + im2])
	app.SetParameterString("out", resultspath + satbandmathimage)
	app.SetParameterString("exp", expression)
	app.ExecuteAndWriteOutput()

	filelist = [inputsfile, resultspath + satbandmathimage]

#-------------------------------------------------------------------------------
# step 3 - color mapping
#-------------------------------------------------------------------------------
	if(do_colormap == 'true'):
		#get min and max for colormap
		img = gdal.Open(resultspath + satbandmathimage)
		img_stats = img.GetRasterBand(1).GetStatistics(0,1)
		min_val = str(img_stats[0])
		max_val = str(img_stats[1])

		apptype = "ColorMapping"
		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterString("in", resultspath + satbandmathimage)
		app.SetParameterString("method","continuous")
		app.SetParameterString("method.continuous.min", min_val)
		app.SetParameterString("method.continuous.max", max_val)
		app.SetParameterString("method.continuous.lut", cmap)
		app.SetParameterString("out", resultspath + color_satbandmathimage)
		app.ExecuteAndWriteOutput()
		filelist = [inputsfile, resultspath + color_satbandmathimage]

#-------------------------------------------------------------------------------
# step 4 - file transfer
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
