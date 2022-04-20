# ORFEO Toolbox
# otb_sentinel_bandoperations.py
#--------------------------------------------------------------
# band math on the sentinel image data
# get sentinel data via planet lab
# or directly from sentinel and convert .jp2 to geotif (.tif)

# urban build up band Band operations
# set the image names in the settings file

# Normalised Difference Built-up Index (NDBI)
# Index based Built-up index (IBI)
# Urban Index (UI)
# New Built-up Index (NBI)
# source: VIVEK: A New Three Band Index for Identifying Urban Areas using Satellite Images

# General comments
# Input images must share same origin, spacing, size, projection
# Select / set the settings in the settings.txt file !
# Activate the OTB conda environment before you run this code
# conda activate OTB
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
	# print command line arguments
	for arg in sys.argv[1:]:
		print ("This the selected input: ", arg)

	changetype = arg.strip()
	if((changetype == 'ibi') or (changetype  == 'nbi') or (changetype  == 'ui') or (changetype  == 'ndbi')):
		print("\nProceeding to create change map with: ", changetype)
		create_change_map(changetype)
	else:
		print("\nOnly ibi, nbi, ui or ndbi operations possible... Try again.\n")
		exit()
#------------------------------------------------------------------------------

def create_change_map (changetype):
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
	# step 1 - preparation - copy the selected sentineldata to the raster folder and uncompress

	rastershapezipfile =  'area2_0717_2017_sentinel2.zip'
	shutil.copy(collectionpath + rastershapezipfile, rasterpath)
	with zipfile.ZipFile(rasterpath + rastershapezipfile, 'r') as zip_ref:
		zip_ref.extractall(rasterpath)

	print("Selected zipped files moved to vector directory and unzipped..")
	parts = rastershapezipfile.split('_')
	token = parts[2] + parts[1]
	ext = '.tif'
	c_ext = '.png'
	do_colormap = 'true'
	cmap = 'relief'				#'hsv'	'jet'

	#---------------------------------------------------------------------------
	# step 2  - band operations
	#---------------------------------------------------------------------------
	if(changetype == 'ndbi'):
		print("\nIndex based Built-up index\n")

		# B11, B8A both have 20m resolution
		im1 = findband('B11', token, ext, sentinelrasterpath)
		im2 = findband('B8A', token, ext, sentinelrasterpath)
		print('This is the swir band: ', im1)
		print('This is the nir band: ', im2)

		apptype = "BandMathX"

		sentinelbandmathimage = 'sentinel2_' + changetype +  '_' + token + ext
		color_sentinelbandmathimage = 'color_sentinel2_' + changetype + '_' + token + c_ext

		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterStringList("il", [sentinelrasterpath + im1, sentinelrasterpath + im2])
		expression = "(im1b1 - im2b1) / (im1b1 + im2b1)"
		app.SetParameterString("out", resultspath + sentinelbandmathimage)
		app.SetParameterString("exp", expression)
		app.ExecuteAndWriteOutput()

		filelist = [inputsfile, resultspath + sentinelbandmathimage]

	#---------------------------------------------------------------------------
	elif(changetype == 'ui'):
		print("\nPerforming Urban Index\n")

		#B04 has 10m resolution
		#B11 has 20m resolution

		im1_s = findband('B11', token, ext, sentinelrasterpath)
		im2_10m = findband('B04', token, ext, sentinelrasterpath)
		print('This is the swir band: ', im1_s)
		print('This is the nir band: ', im2_10m)


		#check resolutions
		#print(gdal.Info(sentinelrasterpath + im1))
		#print(gdal.Info(sentinelrasterpath + im2_10m))

		#print('\n\n')
		#minx1, miny1, maxx1, maxy1 = get_minmax_points(sentinelrasterpath, im1)
		#print(minx1, miny1, maxx1, maxy1)
		#minx2, miny2, maxx2, maxy2 = get_minmax_points(sentinelrasterpath, im2_10m)
		#print(minx2, miny2, maxx2, maxy2)
		#print('\n\n')

                #convert B04 to 20m resolution
		im2_parts = im2_10m.split(ext)
		im2_s = im2_parts[0] + '_20m_' + ext
		ds = gdal.Warp(sentinelrasterpath + im2_s, sentinelrasterpath + im2_10m, xRes=20, yRes=20)
		ds = None

		rasterarray = [im1_s, im2_s]
		minx, miny, maxx, maxy = get_minmax_points_multiple(sentinelrasterpath, rasterarray)
		print('Here are the min points: ', minx, miny, maxx, maxy)
		print('\n\n')

		# https://stackoverflow.com/questions/48531082/cropping-a-raster-file-using-gdal-w-python
		# crop larger image B11
		#window = (minx, miny, maxx, maxy)

		window = (281020, 9091640, 294960, 9079480)
		print(window)

		im1 = 'crop_' + im1_s
		gdal.Translate(sentinelrasterpath + im1, sentinelrasterpath + im1_s, projWin = window)

		im2 = 'crop_' + im2_s
		gdal.Translate(sentinelrasterpath + im2, sentinelrasterpath + im2_s, projWin = window)


		#TRY ----------------------------
		#1 window = [a,b,c,d] NOT (a,b,c,d)
		#2 offset + size
		#window = (offset_x, offset_y, size_x, size_y)
		#gdal.Translate('output_crop_raster.tif', 'input_raster.tif', srcWin = window)

		#https://sites.google.com/site/rlgnotes/home/cropping-and-editing
		#https://www.geos.ed.ac.uk/~smudd/TopoTutorials/html/tutorial_raster_conversion.html
		#gdalwarp -te <x_min> <y_min> <x_max> <y_max> input.bil clipped_output.bil


		'''
		print('\n\n')
		minx1, miny1, maxx1, maxy1 = get_minmax_points(sentinelrasterpath, im1)
		print(minx1, miny1, maxx1, maxy1)
		minx2, miny2, maxx2, maxy2 = get_minmax_points(sentinelrasterpath, im2_10m)
		print(minx2, miny2, maxx2, maxy2)
		print('\n\n')



		im1_check = gdal.Open(sentinelrasterpath + im1)
		_, xres, _, _, _, yres  = im1_check.GetGeoTransform()
		print('\n\nIMAGE1: ', xres, yres)

		im2_10m_check = gdal.Open(sentinelrasterpath + im2_10m)
		_, xres, _, _, _, yres  = im2_10m_check.GetGeoTransform()
		print('IMAGE2: ', xres, yres)
		
		#convert B04 to 20m resolution
		im2_parts = im2_10m.split(ext)
		im2 = im2_parts[0] + '_20m_' + ext
		ds = gdal.Warp(sentinelrasterpath + im2, sentinelrasterpath + im2_10m, xRes=20, yRes=20)
		ds = None
		'''

		
		#check resolutions
		print('\n\n')
		print('im1: ', im1)
		print('im2: ', im2)
		print('\n\n')
		print(gdal.Info(sentinelrasterpath + im1))
		print(gdal.Info(sentinelrasterpath + im2))
		'''


		apptype = "BandMathX"

		sentinelbandmathimage = 'sentinel2_' + changetype +  '_' + token + ext
		color_sentinelbandmathimage = 'color_sentinel2_' + changetype + '_' + token + c_ext

		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterStringList("il", [sentinelrasterpath + im1, sentinelrasterpath + im2])
		expression = "(im1b1 - im2b1) / (im1b1 + im2b1)"
		app.SetParameterString("out", resultspath + sentinelbandmathimage)
		app.SetParameterString("exp", expression)
		app.ExecuteAndWriteOutput()

		filelist = [inputsfile, resultspath + sentinelbandmathimage]

	#--------------------------------------------------------------------------
	elif(changetype == 'nbi'):
		print("\nNew Built-Up Index\n")

		im1 = findband('B04', token, ext, sentinelrasterpath)
		im2 = findband('B11', token, ext, sentinelrasterpath)
		im3 = findband('B08', token, ext, sentinelrasterpath)
		print('This is the red band: ', im1)
		print('This is the mir band: ', im2)
		print('This is the nir band: ', im3)

		apptype = "BandMathX"

		sentinelbandmathimage = 'sentinel2_' + changetype +  '_' + token + ext
		color_sentinelbandmathimage = 'color_sentinel2_' + changetype + '_' + token + c_ext

		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterStringList("il", [sentinelrasterpath + im1, sentinelrasterpath + im2])
		expression = "(im1b1 * im2b1) / im3b1"
		app.SetParameterString("out", resultspath + sentinelbandmathimage)
		app.SetParameterString("exp", expression)
		app.ExecuteAndWriteOutput()

		filelist = [inputsfile, resultspath + sentinelbandmathimage]

#-------------------------------------------------------------------------------
# step 3 - color mapping
#-------------------------------------------------------------------------------
	if(do_colormap == 'true'):
		#get min and max for colormap
		img = gdal.Open(resultspath + sentinelbandmathimage)
		img_stats = img.GetRasterBand(1).GetStatistics(0,1)
		min_val = str(img_stats[0])
		max_val = str(img_stats[1])

		apptype = "ColorMapping"
		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterString("in", resultspath + sentinelbandmathimage)
		app.SetParameterString("method","continuous")
		app.SetParameterString("method.continuous.min", min_val)
		app.SetParameterString("method.continuous.max", max_val)
		app.SetParameterString("method.continuous.lut", cmap)
		app.SetParameterString("out", resultspath + color_sentinelbandmathimage)
		app.ExecuteAndWriteOutput()
		filelist = [inputsfile, resultspath + color_sentinelbandmathimage]

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
	'''
#---------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------
