# COCKTAIL
# otb_raster_classify.py
# RTS, March 2022
# updated July, Sept 2022
#---------------------------------------------------------------------------------
# raster classifier training and image classification
# classifiers: Support Vector Machine, Random Forest
# --------------------------------------------------------------------------------
import sys, os
import json
from datetime import datetime
import pytz
from osgeo import gdal
import otbApplication
import numpy
from PIL import Image as PILImage
from pcloud import PyCloud

from helper import *


# Set environment variables
#os.environ['OTB_MAX_RAM_HINT'] = '4096'
os.environ['GDAL_DRIVER_PATH'] = '/home/ghemanth2578/miniconda3/envs/OTB/lib/gdalplugins/'
# os.environ['OTB_LOGGER_LEVEL'] = 'DEBUG'
# Set the GDAL_DRIVER_PATH environment variable
#os.environ['GDAL_DRIVER_PATH'] = '/home/ghemanth2578/miniconda3/envs/OTB/lib/gdalplugins'
# Local path and variables
datapath = '/home/ghemanth2578/cocktail/data/'
inputsfile = datapath + 'settings.txt'

#---------------------------------------------------------------------------------
def main():

	response = ''
	elements = []

	print('\nYou can use this routine to perform Support Vector Machine or Random Forest classification on PlanetLab, Sentinel2 or Landsat8 data')
	print('The raster image shapefiles should be in the collection directory.')
	print('The corresponding compressed shapefile is defined in the settings.txt file.')
	print('Supported classification options are: rf or libsvm')
	print('Enter the name of the raster image, followed by the classifier.')
	print('Example: area2_0612_2020_4bands.tif rf')
	print('If you enter only the classifier choice, the raster image in the settings.txt file will be used.')

	response = input("\nEnter your choices: ")
	input_classifier = ''
	input_rasterimage = ''

	try:
		elements = response.split(' ')
		#print("0: ", elements[0])
		#print("1: ", elements[1])
		if(len(elements) == 2):
			elements = response.split(' ')
			input_rasterimage = elements[0]
			input_classifier = elements[1]
			raster_classify(input_rasterimage, input_classifier)

		elif((len(elements) == 1) and ((elements[0] == 'rf') or (elements[0] == 'libsvm'))):
			input_classifier = elements[0]
			raster_classify(input_rasterimage, input_classifier)
		else:
			print('\Input error... try again..')
			exit()
	except:
		print('\nSomething went wrong... try again...')
		exit()

#---------------------------------------------------------------------------------

def raster_classify (input_rasterimage, input_classifier):
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
		rasterimage = jdata['rasterimage']
		rastershapezipfile = jdata['rastershapezipfile']
		rasterpath = jdata['rasterpath']
		vectorpath = jdata['vectorpath']
		resultspath = jdata['resultspath']
		collectionpath = jdata['collectionpath']
		colortemplate = jdata['colortemplate']
		cfieldname = jdata['cfieldname']

		stats_save = jdata['stats_save']
		t2p = jdata['T2P']
		pdir = jdata['pdir']
		r_height = int(jdata['r_height'])
		r_width = int(jdata['r_width'])
		background = jdata['background']
		location = jdata['location']
		addcolor = jdata['raster_addcolor']

	if(input_rasterimage == ''):
		pass
	else:
		rasterimage = input_rasterimage

	rimage = rasterpath + rasterimage
	key = ".zip"
	s = rastershapezipfile.split(key)
	sf = s[0] + ".shp"
	sfile = vectorpath + sf
	print('\nShape file Path: ', sfile)
	print('\nRaster Image Path: ',rimage)

	print('\n\nHere are the inputs')
	print('Rasterimage: ', rasterimage)
	print('Raster shapefiles: ', rastershapezipfile)
	print('Raster shapefile (.shp): ', sf)
	print('Classifier: ', input_classifier)

	b_rimage = rasterimage.split('.tif')[0] + '_'

#-----------------------------------------------------------------------------
	# step 1 - preparation 
	print('moving data from collection to the vectorfiles and rasterimages...')

	try:
		print('\n Collection Path: ',collectionpath + rasterimage)
		print('\n RasterImage Path: ', rasterpath + rasterimage)
		shutil.copy(collectionpath +  rasterimage, rasterpath + rasterimage)
	except:
		print('\nCant find the raster image... Try again...')
		exit()

	try:
		print(collectionpath + rastershapezipfile)
		shutil.copy(collectionpath + rastershapezipfile, vectorpath + rastershapezipfile)

	except:
		print('\nCant find the vector data ... Check settings...')
		exit()

	with zipfile.ZipFile(vectorpath + rastershapezipfile, 'r') as zip_ref:
  		zip_ref.extractall(vectorpath)

	print("Selected zipped files moved to vector directory and unzipped..")

#------------------------------------------------------------------------------
	#step 2 - train a classifiers with the raster input image and the shapefile with ROIs

	apptype = "TrainImagesClassifier"
	samplemv = 100
	samplemt = 100
	samplevtr = 0.5

	classifier = input_classifier

	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterStringList("io.il", [rimage])
	app.SetParameterStringList("io.vd", [sfile])
	app.SetParameterString("sample.vfn", jdata['cfieldname'])
	app.SetParameterInt("sample.mv", samplemv)
	app.SetParameterInt("sample.mt", samplemt)
	app.SetParameterFloat("sample.vtr", samplevtr)
	app.SetParameterString("classifier", classifier)

	tstamp = create_timestamp(location)
	
	#Random Forest
	if (classifier == 'rf'):
		print('\n\n Training Random Forest Model\n\n')
		modelname = jdata['modelname_rf']
		app.SetParameterString("io.out", resultspath + modelname)
		classified_rimage = b_rimage + tstamp + '_' + jdata['classified_rimage_rf']
		con_matrix = jdata['confusion_matrix_rf']
		app.SetParameterInt("classifier.rf.max", int(jdata['rf_max']))
		app.SetParameterInt("classifier.rf.min", int(jdata['rf_min']))
		app.SetParameterInt("classifier.rf.ra", int(jdata['rf_ra']))
		app.SetParameterInt("classifier.rf.cat", int(jdata['rf_cat']))
		app.SetParameterInt("classifier.rf.var", int(jdata['rf_var']))
		app.SetParameterInt("classifier.rf.nbtrees", int(jdata['rf_ntrees']))
		app.SetParameterFloat("classifier.rf.acc", float(jdata['rf_acc']))
		
	#Support Vector Machine
	elif(classifier == 'libsvm'):
		print('\n\n Training Support Vector Machine Model\n\n')
		modelname =  jdata['modelname_svm']
		app.SetParameterString("io.out", resultspath + modelname)
		classified_rimage = b_rimage + tstamp + '_' + jdata['classified_rimage_svm']
		con_matrix =  jdata['confusion_matrix_svm']
		app.SetParameterString("classifier.libsvm.k", jdata['svm_k'])
		app.SetParameterFloat("classifier.libsvm.c", float(jdata['svm_c']))
		app.SetParameterString("classifier.libsvm.opt", jdata['svm_opt'])

	app.SetParameterString("io.confmatout", resultspath + con_matrix)
	app.ExecuteAndWriteOutput()

#--------------------------------------------------------------------------------
	#step 3  - classify an input image with the trained model

	apptype = "ImageClassifier"
	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterString("in", rimage)
	app.SetParameterString("model", resultspath + modelname)
	app.SetParameterString("out", resultspath + classified_rimage)
	app.ExecuteAndWriteOutput()

#--------------------------------------------------------------------------------
	#step 4 - calculate classifier statistics

	stats, fname = get_classifier_statistics(location, resultspath, con_matrix, stats_save)
	print('\nHere are the classifier statistics, based on the confusion matrix\n')
	print(stats)
	print('\n')

#-------------------------------------------------------------------------------
	#step 5 - apply colormap

	if(addcolor == "yes"):
		print('\n\nApplying colormap\n')
		apptype = "ColorMapping"
		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterString("in", resultspath + classified_rimage)  		#the output of step 2
		app.SetParameterString("method", "custom")
		app.SetParameterString("method.custom.lut", datapath + colortemplate)

		#add timestamp now..
		tstamp = create_timestamp(location)

		if(classifier == 'libsvm'):
			color_classified_rimage = b_rimage + tstamp + '_' + jdata['classified_rimage_color_svm']
		elif(classifier == 'rf'):
			color_classified_rimage = b_rimage + tstamp + '_' + jdata['classified_rimage_color_rf']

		app.SetParameterString("out", resultspath + color_classified_rimage)
		app.ExecuteAndWriteOutput()

#-------------------------------------------------------------------------------
	#step 6 - update settings file with user inputs

	imagetoken = jdata['input_rasterimage']
	classifiertoken = jdata['input_classifier']

	#read in the data from the settings file
	try:
		f = open(inputsfile, 'r')
		data = f.readlines()
		c = 0
		for line in data:
			if(imagetoken in line):
				imagereplacement = line.replace(imagetoken, rasterimage)
				iline = c
				#print(imagereplacement)
			elif(classifiertoken in line):
				classificationreplacement = line.replace(classifiertoken, input_classifier)
				cline = c
				#print(classificationreplacement)
			c = c+1
		f.close()

	except:
		print('settings file error...')

	#write out the data to the updated settings file
	try:

		inputsfile_updated = datapath + 'settings_updated.txt'
		f = open(inputsfile_updated, 'w')
		cc = 0
		for line in data:
			if(cc == iline):
				f.write(imagereplacement)
			elif(cc == cline):
				f.write(classificationreplacement)
			else:
				f.write(line)
			cc = cc+1
		f.close()
		print('\nUpdated settings file saved...')

	except:
		print('Updated settings file error...')
		exit()

#-------------------------------------------------------------------------------
	#step 7 - transfer to storage (pCloud)

	if(t2p == "yes"):
		f = open(authfile, 'r')
		lines = f.readlines()
		username = lines[0].strip()
		password = lines[1].strip()
		f.close()

		#zip up the settings and stats (classifier precision, recall and fscore calculated from the confusion matrix)
		stats_settings = jdata['stats+settings']
		tstamp = create_timestamp(location)
		stats_settings_tstamp = stats_settings.split('.zip')[0] + '_' + tstamp + '.zip'
		zipOb = ZipFile(resultspath + stats_settings_tstamp, 'w')
		zipOb.write(resultspath + fname)
		zipOb.write(inputsfile_updated)			#use the updated file

		zipOb.write(inputsfile)
		zipOb.close()

		conn = PyCloud(username, password, endpoint='nearest')
		if(addcolor == "yes"):
			filelist = [resultspath + color_classified_rimage, resultspath + stats_settings_tstamp]
		else:
			filelist = [resultspath + classified_rimage, resultspath + stats_settings_tstamp]

		conn.uploadfile(files=filelist, path=pdir)
		print('\n\nUploaded: ' , filelist)
		print('\n\n')

#---------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------
