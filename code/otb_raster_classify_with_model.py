# COCKTAIL
# otb_raster_classify_with_model.py
# RTS, October 2022
#---------------------------------------------------------------------------------
# raster classification based on pretrained model
# classifier models: Support Vector Machine, Random Forest

# Todo: add the confidence map output:
# https://www.orfeo-toolbox.org/CookBook/Applications/app_ImageClassifier.html

# --------------------------------------------------------------------------------
import sys, os
import json
from datetime import datetime
import pytz
import gdal
import otbApplication
import numpy
from PIL import Image as PILImage
from pcloud import PyCloud

from helper import *

# Local path and variables
datapath = '/home/marcbohlen/cocktail/data/'
inputsfile = datapath + 'settings.txt'

#---------------------------------------------------------------------------------
def main():

	response = ''
	elements = []

	print('\nYou can use this routine to peform classification on PlanetLab, Sentinel2 or Landsat8 data with a preexisting model')
	print('The raster images should be in the collection directory, and the model should reside in the results diretory.')
	print('Supported classification mdoels are: rf (RandomForest or libsvm (Support Vector Machines)')
	print('Enter the name of the raster image, followed by the name of the model.')
	print('Example: area2_0612_2020_4bands.tif model_rf.model')

	response = input("\nEnter your choices: ")
	input_modelname = ''
	input_rasterimage = ''

	try:
		elements = response.split(' ')
		if(len(elements) == 2):
			elements = response.split(' ')
			input_rasterimage = elements[0]
			input_modelname = elements[1]
			raster_classify(input_rasterimage, input_modelname)

		else:
			print('\Input error...Expecting two inputs...')
			exit()
	except:
		print('\nSomething went wrong... try again...')
		exit()

#---------------------------------------------------------------------------------

def raster_classify (input_rasterimage, input_modelname):
	try:
        	f = open(inputsfile, 'r')
        	data = f.read()
        	jdata = json.loads(data)
        	f.close()
	except:
        	print('\n...data access error...\n')
	else:
		#print(jdata)
		print("Reading in settings ok.")
		authfile = jdata['authfile']
		#rasterimage = jdata['rasterimage']
		rasterpath = jdata['rasterpath']
		resultspath = jdata['resultspath']
		collectionpath = jdata['collectionpath']
		colortemplate = jdata['colortemplate']
		cfieldname = jdata['cfieldname']

		t2p = jdata['T2P']
		pdir = jdata['pdir']
		r_height = int(jdata['r_height'])
		r_width = int(jdata['r_width'])
		background = jdata['background']
		location = jdata['location']
		addcolor = jdata['raster_addcolor']


	rimage = rasterpath + input_rasterimage
	modelname = resultspath + input_modelname
	
	print('\n\nHere are the inputs')
	print('Rasterimage: ', rimage)
	print('Model: ', modelname)
	b_rimage = input_rasterimage.split('.tif')[0] + '_'

#-----------------------------------------------------------------------------
	#step 2 - classify with pretrained model

	tstamp = create_timestamp(location)
	cparts = input_modelname.split('_')
	
	if(len(cparts) == 2):
		classifier_model = input_modelname.split('_')[1]
		classifier = classifier_model.split('.model')[0]
	elif(len(cparts) == 3):
		classifier_model = cparts[2]
		classifier = cparts[2].split('.model')[0]
	
	#print('Classifier model: ', classifier_model)
	confidencemap = jdata['confidencemap']	
	print('Confidence map: ', confidencemap)
	
	#Random Forest
	if ('rf' in classifier_model):
		classified_rimage = b_rimage + tstamp + '_' + jdata['classified_rimage_rf']

	#Support Vector Machine
	elif('svm' in classifier_model):
		classifier = 'lib' + classifier_model.split('.model')[0]
		classified_rimage = b_rimage + tstamp + '_' + jdata['classified_rimage_svm']

	apptype = "ImageClassifier"
	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterString("in", rimage)
	app.SetParameterString("model", modelname)
	#new
	app.SetParameterString("confmap", resultspath + confidencemap)
	app.SetParameterString("out", resultspath + classified_rimage)
	app.ExecuteAndWriteOutput()

#-------------------------------------------------------------------------------
	#step 3 - apply colormap

	if(addcolor == "yes"):
		print('\n\nApplying colormap\n')
		apptype = "ColorMapping"
		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterString("in", resultspath + classified_rimage)  		#the output of step 2
		app.SetParameterString("method", "custom")
		app.SetParameterString("method.custom.lut", datapath + colortemplate)

		#add timestamp now
		tstamp = create_timestamp(location)

		if(len(cparts) == 3):
			t = cparts[0]
		else:
			t = ''

		if(classifier == 'libsvm'):
			color_classified_rimage = b_rimage + tstamp + '_' + t + '_'  + jdata['classified_rimage_color_svm']
		elif(classifier == 'rf'):
			color_classified_rimage = b_rimage + tstamp + '_' + t + '_' + jdata['classified_rimage_color_rf']

		app.SetParameterString("out", resultspath + color_classified_rimage)
		app.ExecuteAndWriteOutput()

#-------------------------------------------------------------------------------
	#step 4 - transfer only the output image to storage (pCloud)

	if(t2p == "yes"):
		f = open(authfile, 'r')
		lines = f.readlines()
		username = lines[0].strip()
		password = lines[1].strip()
		f.close()

		conn = PyCloud(username, password, endpoint='nearest')
		if(addcolor == "yes"):
			filelist = [resultspath + color_classified_rimage]
		else:
			filelist = [resultspath + classified_rimage]

		conn.uploadfile(files=filelist, path=pdir)
		print('\n\nUploaded: ' , filelist)
		print('\n\n')

#---------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------
