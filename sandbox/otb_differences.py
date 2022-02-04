# ORFEO Toolbox 
# otb_differences.py
#--------------------------------------------------------------
# MultivariateAlterationDetector
# Change detection by Multivariate Alteration Detector (MAD) algorithm 
# Activate the OTB conda environment before you run this code
# conda activate OTB
# Inputs set in the settings.txt file
# rasterimage: before state (older image)
# rasterimage2: after state (newer image)
# RTS, Feb 2022
# -------------------------------------------------------------

#CHECK - RadimetricIndices
# https://www.orfeo-toolbox.org/CookBook/Applications/app_RadiometricIndices.html
# CHECK - BandX
# https://www.orfeo-toolbox.org/CookBook/recipes/bandmathX.html#advanced-image-operations-using-bandmathx 


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
	create_change_map()

#------------------------------------------------------------------------------
def create_timestamp(location):
    tz = pytz.timezone(location)
    now = datetime.now(tz)
    current_time = now.strftime("%d-%m-%Y-%H-%M")
    return(current_time) 

#------------------------------------------------------------------------------
def create_change_map ():
#inputs set in the setting.txt file

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

	#craete the name here with the dates of the input images
	b_rimage = rasterimage.split('.tif')[0] + '_'

#------------------------------------------------------------------------------

	# Change detection between two multispectral images using the Multivariate Alteration Detector (MAD) algorithm
	# https://www.orfeo-toolbox.org/CookBook/Applications/app_MultivariateAlterationDetector.html
	# Input images 1 and 2 should share exactly the same origin, spacing, size, and projection if any.
	
	# differencing
	apptype = "MultivariateAlterationDetector"

	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterString("in1", rimage)
	app.SetParameterString("in2", rimage2) #after, newer image
	app.SetParameterString("out", resultspath + changeimage)
	#tstamp = create_timestamp(location)

	app.ExecuteAndWriteOutput()

	#thresholding
	# https://github.com/orfeotoolbox/OTB-Documents/blob/master/Courses/2014-OGRS/multitemp.org
 	# https://www.orfeo-toolbox.org/CookBook/Applications/app_BandMath.html

	apptype = "BandMath"
	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterStringList("il", [resultspath + changeimage])
	app.SetParameterString("out", resultspath + bandmathchangeimage)
	app.SetParameterString("exp", bandmathexpression) #defined in the settings

	app.ExecuteAndWriteOutput()
	
	'''
	#NDVI difference
	# https://www.youtube.com/watch?v=Q9kgA2BGs4E
	apptype = "BandMathX" 
	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterStringList("il", [rimage, rimage2])
	app.SetParameterString("out", resultspath + bandmathchangeimage)
	#app.SetParameterString("exp", bandmathexpression) #defined in the settings
	#app.SetParameterString("exp", "(ndvi(im1b1,im1b4) - ndvi(im2b1,im2b4)) > 0.20 ? 255:0")
	app.SetParameterString("exp", "((im2b1 / im1b1) / (im2b1 + im1b1))*256")
	app.ExecuteAndWriteOutput()
	'''
#---------------------------------------------------------------------------------
	#step 2 - transfer to storage (pCloud)

	if(t2p == "yes"):
		f = open(authfile, 'r')
		lines = f.readlines()
		username = lines[0].strip()
		password = lines[1].strip()
		f.close()

		conn = PyCloud(username, password, endpoint='nearest')
		filelist = [inputsfile, resultspath + bandmathchangeimage]

		conn.uploadfile(files=filelist, path=pdir)
		print('\n\nUploaded: ' , filelist)
		print('\n\n')
#---------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------
