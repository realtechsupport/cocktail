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
# -------------------------------------------------------------

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
#-------------------------------------------------------------
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

	type = arg.strip()

	if(type == 'ndbi'):
		print("\nProceeding with NDBI index")
		create_change_map(type)
	else:
		print("\nOnly ibi, nbi, ui or ndbi operations possible... Try again.\n")
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

	#rastershapezipfile =  'area2_0726_2021_sentinel2.zip'
	rastershapezipfile = 'area2_0727_2021_landsat8.zip'



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
	if(changetype == 'ndbi'):
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
	#---------------------------------------------------------------------------
	'''
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

		#check resolutions
		print('\n\n')
		print('im1_s: ', im1_s)
		print('im2_s: ', im2_s)
		print('\n\n')
		print(gdal.Info(sentinelrasterpath + im1_s))
		print(gdal.Info(sentinelrasterpath + im2_s))


		#now try with gdal.Warp
		#https://gis.stackexchange.com/questions/45053/gdalwarp-cutline-along-with-shapefile
		#move and unpack the shapefile to the ROI dir in the vectorpath
		roishapezipfile =  'area2_shape_crop.zip'
		roishape = roishapezipfile.split('.zip')[0] + '.shp'
		roipath = vectorpath + 'roi/'
		shutil.copy(collectionpath + roishapezipfile, roipath)
		with zipfile.ZipFile(roipath + roishapezipfile, 'r') as zip_ref:
			zip_ref.extractall(roipath)


		ds = gdal.Warp(sentinelrasterpath + im1, sentinelrasterpath + im1_s, cutlineDSname = roipath+roishape)
		ds = None
		#ds = gdal.Warp(-cutline roipath+roishape -crop_to_cutline sentinelrasterpath+im2_s sentinelrasterpath+im2)
		#ds = None

		print('\n\nim1\n')
		print(gdal.Info(sentinelrasterpath + im1))
		#print('\n\nim2\n')
		#print(gdal.Info(sentinelrasterpath + im2))


		rasterarray = [im1_s, im2_s]
		minx, miny, maxx, maxy = get_minmax_points_multiple(sentinelrasterpath, rasterarray)
		print('Here are the min points: ', minx, miny, maxx, maxy)
		print('\n\n')

		# https://stackoverflow.com/questions/48531082/cropping-a-raster-file-using-gdal-w-python
		# crop larger image B11
		#window = (minx, miny, maxx, maxy)

		#projWin
		pwindow = [281020, 9091650, 294960, 9079470]
		#srcWin
		#swindow = [20, 10, 13920, 12140]

		im1 = 'crop_' + im1_s
		ds = gdal.Open(sentinelrasterpath + im1_s)
		gdal.Translate(sentinelrasterpath + im1, ds, projWin = pwindow)
		#gdal.Translate(sentinelrasterpath + im1, ds, srcWin = swindow)
		ds = None

		#swindow = [20, 20, 13930, 12150]
		pwindow = [281020, 9091650, 294960, 9079470]
		im2 = 'crop_' + im2_s
		ds = gdal.Open(sentinelrasterpath +im2_s)
		gdal.Translate(sentinelrasterpath + im2, ds, projWin = pwindow)
		#gdal.Translate(sentinelrasterpath + im2, ds, srcWin = swindow)
		ds = None

		#TRY ----------------------------
		#1 window = [a,b,c,d] NOT (a,b,c,d)
		#2 offset + size
		#window = (offset_x, offset_y, size_x, size_y)
		#gdal.Translate('output_crop_raster.tif', 'input_raster.tif', srcWin = window)

		#https://sites.google.com/site/rlgnotes/home/cropping-and-editing
		#https://www.geos.ed.ac.uk/~smudd/TopoTutorials/html/tutorial_raster_conversion.html
		#gdalwarp -te <x_min> <y_min> <x_max> <y_max> input.bil clipped_output.bil

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

		#check resolutions
		print('\n\n')
		print('im1: ', im1)
		print('im2: ', im2)
		print('\n\n')
		print(gdal.Info(sentinelrasterpath + im1))
		print(gdal.Info(sentinelrasterpath + im2))


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

	'''
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
