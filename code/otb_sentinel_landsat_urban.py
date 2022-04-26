# ORFEO Toolbox
# otb_sentinel_landsat_urban.py
#--------------------------------------------------------------
# band math on the sentinel image data
# get sentinel data via planet lab
# or directly from sentinel and convert .jp2 to geotif (.tif)
#
# get landsat data from https://earthexplorer.usgs.gov/
# urban build up band Band operations

# Normalised Difference Built-up Index (NDBI)

# General comments
# Input images must share same origin, spacing, size, projection
# Select / set the settings in the settings.txt file !
# Activate the OTB conda environment before you run this code
# conda activate OTB
# RTS, April 2022
# ------------------------------------------------------------------------

#Landsat bands
# https://www.usgs.gov/faqs/what-are-band-designations-landsat-satellites

#Sentinel bands
# https://gisgeography.com/sentinel-2-bands-combinations/

'''
ndbi on Sentinel:
swir: B11
nir: B08A
operation: (B11 − B8A) / ( B11 + B8A)

ndbi on Landsat8: 
swir1: B06
nir: B05
operation: (B06 - B05) / (B06 + B05)

'''
#----------------------------------------------------------------------------
import sys, os
import json
import gdal
import otbApplication
import numpy
from PIL import Image as PILImage
from pcloud import PyCloud
from zipfile import ZipFile

from helper import *

# select the input: Sentinel or Landsat -------------------------------------
rastershapezipfile =  'area2_0726_2021_sentinel2.zip'
#rastershapezipfile = 'area2_0727_2021_landsat8.zip'


# Local path and variables
datapath = '/home/blc/cocktail/data/'
inputsfile = datapath + 'settings.txt'
#------------------------------------------------------------------------------

def main():
	# print command line arguments
	for arg in sys.argv[1:]:
		print ("This the selected input: ", arg)

	type = arg.strip()

	if(type == 'ndbi'):
		print("\nProceeding with NDBI index")
		create_change_map(type)
	else:
		print("\nOnly ndbi operation possible... Try again.\n")
		exit()
#------------------------------------------------------------------------------

def create_change_map (type):
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
	# step 1 - preparation - copy the selected Sentinel or Landsat data to the raster folder and uncompress

	if('landsat8' in rastershapezipfile):
		satrasterpath = landsat8rasterpath
	else:
		satrasterpath = sentinelrasterpath

	shutil.copy(collectionpath + rastershapezipfile, satrasterpath)
	with zipfile.ZipFile(satrasterpath + rastershapezipfile, 'r') as zip_ref:
		zip_ref.extractall(satrasterpath)

	print("Selected zipped files moved to vector directory and unzipped..")

	parts = rastershapezipfile.split('_')
	satname = parts[-1].split('.zip')[0]
	token = parts[2] + parts[1]
	ext = '.tif'
	c_ext = '.png'
	do_colormap = 'true'
	cmap = 'relief'				#'hsv'	'jet'

	#---------------------------------------------------------------------------
	# step 2  - band operations
	#---------------------------------------------------------------------------
	if(type == 'ndbi'):
		print("\nNormalized Difference Built-up Index\n")
		# select the appropriate bands
		if('landsat8' in rastershapezipfile):
			nirband = 'B5'
			swirband = 'B6'
		else:
			nirband = 'B8A'
			swirband = 'B11'

		im1 = findband(swirband, token, ext, satrasterpath)
		im2 = findband(nirband, token, ext, satrasterpath)

		print('This is the swir band: ', im1)
		print('This is the nir band: ', im2)
		print('\n\n')

		apptype = "BandMathX"

		satbandmathimage = satname + '_' + type +  '_' + token + ext
		color_satbandmathimage = 'color_' + satname + '_' + type + '_' + token + c_ext

		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterStringList("il", [satrasterpath + im1, satrasterpath + im2])
		expression = "(im1b1 - im2b1) / (im1b1 + im2b1)"
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
