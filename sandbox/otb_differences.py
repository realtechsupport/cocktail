# ORFEO Toolbox
# otb_differences.py
#--------------------------------------------------------------
# change detection - various approches
# MAD
# Change detection between two multispectral images using the Multivariate Alteration Detector (MAD) algorithm
# https://www.orfeo-toolbox.org/CookBook/Applications/app_MultivariateAlterationDetector.html
# Input images 1 and 2 should share exactly the same origin, spacing, size, and projection if any.
# Inputs set in the settings.txt file
# rasterimage: before state (older image)
# rasterimage2: after state (newer image)

# Activate the OTB conda environment before you run this code
# conda activate OTB
# RTS, Feb 2022
# -------------------------------------------------------------
# Radiometric Indeces
# https://www.orfeo-toolbox.org/CookBook/Applications/app_RadiometricIndices.html
# https://www.orfeo-toolbox.org/SoftwareGuide/SoftwareGuidech12.html

# Thresholding
# https://github.com/orfeotoolbox/OTB-Documents/blob/master/Courses/2014-OGRS/multitemp.org
# https://www.orfeo-toolbox.org/CookBook/Applications/app_BandMath.html
# https://github.com/orfeotoolbox/OTB-Documents/blob/master/Courses/2014-OGRS/mvdapps.org
#-------------------------------------------------------------
import sys, os
import json
from datetime import datetime
import pytz
import gdal
import otbApplication
import numpy
from PIL import Image as PILImage
from pcloud import PyCloud
from zipfile import ZipFile

from helper import *

# Local path and variables
datapath = '/home/blc/gdal-otb-qgis-combo/data/'
inputsfile = datapath + 'settings.txt'
#------------------------------------------------------------------------------
def main():
	#changetype = 'simple_ndvi' 
	#changetype = 'multivariatedetector'
	changetype =  'radiometricindices'

	create_change_map(changetype)
#------------------------------------------------------------------------------
def create_timestamp(location):
    tz = pytz.timezone(location)
    now = datetime.now(tz)
    current_time = now.strftime("%d-%m-%Y-%H-%M")
    return(current_time)

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
		authfile = jdata['authfile']
		rasterimage = jdata['rasterimage']
		rasterimage2 = jdata['rasterimage2']
		changeimage = jdata['changeimage']
		bandmathchangeimage = jdata['bandmathchangeimage']
		bandmathexpression = jdata['bandmathexpression']
		rasterpath = jdata['rasterpath']
		resultspath = jdata['resultspath']
		#colortemplate = jdata['colortemplate']

		t2p = jdata['T2P']
		pdir = jdata['pdir']
		r_height = int(jdata['r_height'])
		r_width = int(jdata['r_width'])
		background = jdata['background']
		location = jdata['location']

	rimage = rasterpath + rasterimage
	rimage2 = rasterpath + rasterimage2

	print('\nHere are the inputs')
	print('Before...image 1: ', rasterimage)
	print('After... image 2: ', rasterimage2)
	print('Here is the band math expression: ', bandmathexpression)
	print('\n')

	#create the name here with the dates of the input images
	b_rimage = rasterimage.split('.tif')[0] + '_'

	filelist = []
#------------------------------------------------------------------------------
	if(changetype == 'multivariatedetector'):
		print("\nPerforming multivariatedetector\n")
		apptype = "MultivariateAlterationDetector"
		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterString("in1", rimage)
		app.SetParameterString("in2", rimage2) #after, newer image
		app.SetParameterString("out", resultspath + changeimage)
		app.ExecuteAndWriteOutput()
		filelist = [inputsfile, resultspath + changeimage]
	#--------------------------------------------------------------------------
	elif(changetype == 'simple_ndvi'):
		print("\nPerforming simple_ndvi\n")
		apptype = "BandMathX"
		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterStringList("il", [rimage, rimage2])
		app.SetParameterString("out", resultspath + bandmathchangeimage)
		app.SetParameterString("exp", "(ndvi(im1b1,im1b4) - ndvi(im2b1,im2b4))")
		app.ExecuteAndWriteOutput()

		apptype = "ColorMapping"
		c_out = "ndvi_diff_colormap.png"
		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterString("in", resultspath + bandmathchangeimage)

		app.SetParameterString("method","continuous")
		app.SetParameterString("method.continuous.min", "-0.3")	#min value is -0.6
		app.SetParameterString("method.continuous.max", "0.7")	#max is 0.7
		app.SetParameterString("method.continuous.lut", "jet")
		app.SetParameterString("out", resultspath + c_out)
		filelist = [inputsfile, resultspath + bandmathchangeimage, resultspath + c_out]
	#--------------------------------------------------------------------------
	elif(changetype == 'radiometricindices'):
		print("\nPerforming radiometric based difference image\n")
		apptype = "RadiometricIndices"
		ind_selection = ["Vegetation:NDVI", "Vegetation:TNDVI", "Vegetation:SAVI"]
		#ind_selection = ["Vegetation:NDVI", "Vegetation:RVI", "Vegetation:TNDVI", "Vegetation:SAVI"]
		#ind_selection = ["Vegetation:NDVI"]
		app = otbApplication.Registry.CreateApplication(apptype)

		rm1 = 'RM1.tif'
		rm2 = 'RM2.tif'
		rmdiff = 'RMdifference.tif'

		#operate on first image ... CHECK channels !!!
		app.SetParameterString("in", rimage)
		app.SetParameterString("channels.red", "1")
		app.SetParameterString("channels.green","2")
		app.SetParameterString("channels.blue", "3")
		app.SetParameterString("channels.nir", "4")
		app.SetParameterStringList("list", ind_selection)
		app.SetParameterString("out", resultspath + rm1)
		app.ExecuteAndWriteOutput()

		#operate on second image
		app.SetParameterString("in", rimage2)
		app.SetParameterString("channels.red", "1")
		app.SetParameterString("channels.green","2")
		app.SetParameterString("channels.blue", "3")
		app.SetParameterString("channels.nir", "4")
		app.SetParameterStringList("list", ind_selection)
		app.SetParameterString("out", resultspath + rm2)
		app.ExecuteAndWriteOutput()

		apptype = "BandMathX"
		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterStringList("il", [resultspath + rm1, resultspath + rm2])
		app.SetParameterString("out", resultspath + rmdiff)
		app.SetParameterString("exp", "im2-im1") #ISSUE HERE
		app.ExecuteAndWriteOutput()

		apptype = "ColorMapping"
		c_out = "RMI_diff_colormap.png"
		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterString("in", resultspath + rmdiff)
		app.SetParameterString("method","continuous")
		app.SetParameterString("method.continuous.min", "-0.3")	#check !
		app.SetParameterString("method.continuous.max", "0.7")	#check !
		app.SetParameterString("method.continuous.lut", "jet")
		app.SetParameterString("out", resultspath + c_out)
		app.ExecuteAndWriteOutput()
		filelist = [inputsfile, resultspath + rmdiff, resultspath + c_out]

#---------------------------------------------------------------------------------
	#step 2 - transfer to storage (pCloud)

	if(t2p == "yes"):
		f = open(authfile, 'r')
		lines = f.readlines()
		username = lines[0].strip()
		password = lines[1].strip()
		f.close()

		conn = PyCloud(username, password, endpoint='nearest')
		#filelist = [inputsfile, resultspath + bandmathchangeimage, resultspath + "RMI_differenceimage.tif", resultspath + c_out]
		conn.uploadfile(files=filelist, path=pdir)
		print('\n\nUploaded: ' , filelist)
		print('\n\n')
#---------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------
