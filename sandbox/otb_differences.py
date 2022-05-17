# ORFEO Toolbox
# otb_differences.py
#--------------------------------------------------------------
# change detection - various approches
# 1. MAD
# Change detection between two multispectral images using the Multivariate Alteration Detector (MAD) algorithm
# https://www.orfeo-toolbox.org/CookBook/Applications/app_MultivariateAlterationDetector.html
# rasterimage: before state (older image)
# rasterimage2: after state
# example band math change expression: "im1b4>1.0 ? 255:0"

# 2. Bandmath on a selection of RadiometricIndices
# https://www.orfeo-toolbox.org/CookBook/Applications/app_RadiometricIndices.html
# https://www.orfeo-toolbox.org/SoftwareGuide/SoftwareGuidech12.html

# 3. Bandmath on ndvi index

# General comments
# Input images must share same origin, spacing, size, projection
# Select / set the settings in the settings.txt file !
# Activate the OTB conda environment before you run this code
# conda activate OTB
# RTS, Feb 2022
# -------------------------------------------------------------
# Also: Thresholding
# https://github.com/orfeotoolbox/OTB-Documents/blob/master/Courses/2014-OGRS/multitemp.org
# https://github.com/orfeotoolbox/OTB-Documents/blob/master/Courses/2014-OGRS/mvdapps.org
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
datapath = '/home/blc/gdal-otb-qgis-combo/data/'
inputsfile = datapath + 'settings.txt'
#------------------------------------------------------------------------------

def main():
	# print command line arguments
	for arg in sys.argv[1:]:
		print ("This the selected input: ", arg)

	changetype = arg.strip()
	if((changetype == 'rmi') or (changetype  == 'mad') or (changetype  == 'ndvi')):
		print("\nProceeding to create change map with: ", changetype)
		create_change_map(changetype)
	else:
		print("\nOnly ndvi, mad (multvariatealterationdetector) and rmi (radiometricindices)... Try again.\n")
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
		authfile = jdata['authfile']
		rasterimage = jdata['rasterimage']
		rasterimage2 = jdata['rasterimage2']
		mad_changeimage = jdata['mad_changeimage']
		bandmathchangeimage = jdata['bandmathchangeimage']
		bandmathexpression = jdata['bandmathexpression']
		ndviexpression = jdata['ndviexpression']
		ndvi_diff_color = jdata['ndvi_diff_color']
		
		rmi_ind_selection = jdata['rmi_ind_selection']
		rmi1 = jdata['rmi1']
		rmi2 = jdata['rmi2']
		rmi_diff = jdata['rmi_diff']
		rmi_diff_color = jdata['rmi_diff_color']
		rmi_diff_expression = jdata['rmi_diff_expression']
		colormap_ndvi_min = jdata['colormap_ndvi_min']
		colormap_ndvi_max = jdata['colormap_ndvi_max']
		colormap_ndvi_type = jdata['colormap_ndvi_type']
		colormap_rmi_min = jdata['colormap_rmi_min']
		colormap_rmi_max = jdata['colormap_rmi_max']
		colormap_rmi_type = jdata['colormap_rmi_type']

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
	print('\n')

	filelist = []
	
	#------------------------------------------------------------------------------
	if(changetype == 'mad'):
		print("\nPerforming MultivariateAlterationDetector\n")
		apptype = "MultivariateAlterationDetector"

		#do the alteration detection
		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterString("in1", rimage)
		app.SetParameterString("in2", rimage2) #after, newer image
		app.SetParameterString("out", resultspath + mad_changeimage)
		app.ExecuteAndWriteOutput()

		filelist = [inputsfile, resultspath + mad_changeimage]
	#--------------------------------------------------------------------------
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
