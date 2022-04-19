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

	#-----------------------------------------------------------------------------
	# step 1 - preparation - copy the selected sentineldata to the raster folder and uncompress

	rastershapezipfile =  'area2_0717_2017_sentinel2.zip'
	shutil.copy(collectionpath + rastershapezipfile, rasterpath)
	with zipfile.ZipFile(rasterpath + rastershapezipfile, 'r') as zip_ref:
		zip_ref.extractall(rasterpath)

	print("Selected zipped files moved to vector directory and unzipped..")

	parts = rastershapezipfile.split('_')
	token = parts[2] + parts[1]
	ext = '.tif'
	ext2 = '.png'

	do_colormap = 'true'

	#------------------------------------------------------------------------------
	if(changetype == 'ndbi'):
		print("\nPerforming Normalised Difference Built-up Index\n")

		im1 = findband('B11', token, ext, sentinelrasterpath)
		im2 = findband('B8A', token, ext, sentinelrasterpath)
		print('This is the mir file: ', im1)
		print('This is the nir file: ', im2)

		apptype = "BandMathX"

		sentinelbandmathimage = 'sentinel2_' + changetype +  '_' + token + ext
		color_sentinelbandmathimage = 'color_sentinel2_' + changetype + '_' + token + ext2 

		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterStringList("il", [sentinelrasterpath + im1, sentinelrasterpath + im2])
		expression = "(im1b1 - im2b1) / (im1b1 + im2b1)"
		app.SetParameterString("out", resultspath + sentinelbandmathimage)
		app.SetParameterString("exp", expression)
		app.ExecuteAndWriteOutput()

		filelist = [inputsfile, resultspath + sentinelbandmathimage]
	#--------------------------------------------------------------------------

	'''
	elif(changetype == 'ndvi'):
		print("\nPerforming ndvi\n")
		print('Here is the ndvi expression: ', ndviexpression)

		#do the band math
		apptype = "BandMathX"
		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterStringList("il", [rimage, rimage2])
		app.SetParameterString("out", resultspath + bandmathchangeimage)
		app.SetParameterString("exp", ndviexpression)
		app.ExecuteAndWriteOutput()

		#apply colormap
		apptype = "ColorMapping"
		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterString("in", resultspath + bandmathchangeimage)

		app.SetParameterString("method","continuous")
		app.SetParameterString("method.continuous.min", colormap_ndvi_min)	#min value is -0.6
		app.SetParameterString("method.continuous.max", colormap_ndvi_max)	#max is 0.7
		app.SetParameterString("method.continuous.lut", colormap_ndvi_type)
		app.SetParameterString("out", resultspath + ndvi_diff_color)
		app.ExecuteAndWriteOutput()

		filelist = [inputsfile, resultspath + bandmathchangeimage, resultspath + ndvi_diff_color]

	#--------------------------------------------------------------------------
	elif(changetype == 'rmi'):
		print("\nPerforming Radiometric Based Difference Image\n")
		apptype = "RadiometricIndices"
		#rmi_ind_selection = ["Vegetation:NDVI", "Vegetation:TNDVI", "Vegetation:SAVI"]
		app = otbApplication.Registry.CreateApplication(apptype)

		#operate on first image ... CHECK channels !!!
		app.SetParameterString("in", rimage)
		app.SetParameterString("channels.red", "1")
		app.SetParameterString("channels.green","2")
		app.SetParameterString("channels.blue", "3")
		app.SetParameterString("channels.nir", "4")
		app.SetParameterStringList("list", rmi_ind_selection)
		app.SetParameterString("out", resultspath + rmi1)
		app.ExecuteAndWriteOutput()

		#operate on second image
		app.SetParameterString("in", rimage2)
		app.SetParameterString("channels.red", "1")
		app.SetParameterString("channels.green","2")
		app.SetParameterString("channels.blue", "3")
		app.SetParameterString("channels.nir", "4")
		app.SetParameterStringList("list", rmi_ind_selection)
		app.SetParameterString("out", resultspath + rmi2)
		app.ExecuteAndWriteOutput()

		#do the band math
		apptype = "BandMathX"
		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterStringList("il", [resultspath + rmi1, resultspath + rmi2])
		app.SetParameterString("out", resultspath + rmi_diff)
		app.SetParameterString("exp", rmi_diff_expression) 			#ISSUE HERE
		app.ExecuteAndWriteOutput()

		#colormap
		apptype = "ColorMapping"
		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterString("in", resultspath + rmi_diff)
		app.SetParameterString("method","continuous")
		app.SetParameterString("method.continuous.min", colormap_rmi_min)	#check min !
		app.SetParameterString("method.continuous.max", colormap_rmi_max)	#check max !
		app.SetParameterString("method.continuous.lut", colormap_rmi_type)
		app.SetParameterString("out", resultspath + rmi_diff_color)
		app.ExecuteAndWriteOutput()

		filelist = [inputsfile, resultspath + rmi_diff, resultspath + rmi_diff_color]
'''
#---------------------------------------------------------------------------------
	if(do_colormap == 'true'):

		apptype = "ColorMapping"
		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterString("in", resultspath + sentinelbandmathimage)
		app.SetParameterString("method","continuous")
		app.SetParameterString("method.continuous.min", "0")       #check min !
		app.SetParameterString("method.continuous.max", "255")       #check max !
		app.SetParameterString("method.continuous.lut", 'jet')
		app.SetParameterString("out", resultspath + color_sentinelbandmathimage)
		app.ExecuteAndWriteOutput()
		filelist = [inputsfile, resultspath + color_sentinelbandmathimage]

#---------------------------------------------------------------------------------
	#step 2 - transfer to storage (pCloud)

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
