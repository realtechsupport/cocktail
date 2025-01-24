# COCKTAIL
# otb_raster+texture_classify.py
# raster with haralick texture features classifier training and image classification
# ------------------------------------------------------------------------------
# Random Forest or Support Vector Machine based classification of raster data
# Requires vector based ROI data for training
# Combine with texture map that produces an output with the following texture measures:
# 1-Energy, 2-Entropy, 3-Correlation, 4-Inverse Difference Moment, 5-Inertia, 6-Cluster Shade, 7-Cluster Prominence, 8-Haralick Correlation
# http://wiki.awf.forst.uni-goettingen.de/wiki/index.php/Haralick_Texture
# All pertinent parameters and selections, including the colormap and appropriate ROI vector file are collected
# from the settings.txt file
# Usage: activate OTB (conda activate OTB)
#	 python3 otb_raster+texture_classify.py
#	 > enter choices...
# Updated settings file is saved.
# RTS, March 2022
# Updated July, Sept 2022
# ------------------------------------------------------------------------------

import sys, os
import json
from osgeo import gdal
import otbApplication
import numpy
from PIL import Image as PILImage
from pcloud import PyCloud

from helper import *

# Local path and variables
datapath = '/home/ghemanth2578/cocktaildata/'
inputsfile = datapath + 'settings.txt'

#------------------------------------------------------------------------------
def main():

	response = ''
	elements = []

	print('\nYou can use this routine to perform Support Vector Machine or Random Forest classification on PlanetLab, Sentinel2 or Landsat8 data')
	print('This script will include texture information calculated via Haralick features.')
	print('The raster image and the shapefile vector data should be in the collection directory.')
	print('The corresponding vectordata file is set in the settings.txt file.')
	print('Supported classification options are: rf or libsvm')
	print('Enter the name of the raster image, followed by the classifier.')
	print('Example: area2_0612_2020_4bands.tif rf')
	print('If you enter only the classifier choice, the raster image in the settings.txt file will be used.')

	response = input("\nEnter your choices: ")
	input_classifier = ''
	input_rasterimage = ''

	try:
		elements = response.split(' ')
		if(len(elements) == 2):
			elements = response.split(' ')
			input_rasterimage = elements[0]
			input_classifier = elements[1]
			raster_texture_classify(input_rasterimage, input_classifier)

		elif((len(elements) == 1) and ((elements[0] == 'rf') or (elements[0] == 'libsvm'))):
			input_classifier = elements[0]
			raster_texture_classify(input_rasterimage, input_classifier)
		else:
			print('\Input error... try again..')
			exit()
	except:
		print('\nInput error - enter rastername and classifier or only the classifier (rf or libsvm)')
		exit()

#------------------------------------------------------------------------------
def raster_texture_classify (input_rasterimage, input_classifier):
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
		rastershapezipfile = jdata['rastershapezipfile']
		rasterpath = jdata['rasterpath']
		vectorpath = jdata['vectorpath']
		resultspath = jdata['resultspath']
		collectionpath = jdata['collectionpath']
		colortemplate = jdata['colortemplate']
		cfieldname = jdata['cfieldname']
		texture_map = jdata['texture_map']
		texture_map_3bands = jdata['texture_map_3bands']
		texture_channel = jdata['texture_channel']
		concat_raster_texture = jdata["concat_raster_texture"]

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
		shutil.copy(collectionpath +  rasterimage, rasterpath + rasterimage)
	except:
		print('\nCant find the raster image... Try again...')
		exit()

	try:
		shutil.copy(collectionpath + rastershapezipfile, vectorpath + rastershapezipfile)

	except:
		print('\nCant find the vector data ... Check settings...')
		exit()

	with zipfile.ZipFile(vectorpath + rastershapezipfile, 'r') as zip_ref:
  		zip_ref.extractall(vectorpath)

	print("Selected zipped files moved to vector directory and unzipped..")

#------------------------------------------------------------------------------
	# step 2: get texture information

	apptype = "HaralickTextureExtraction"
	app = otbApplication.Registry.CreateApplication(apptype)
	xrad = 2; yrad = 2
	texture_map = texture_map.split('.tif')[0] + '_chan_' + str(texture_channel) + '.tif'
	app.SetParameterString("in", rimage)
	app.SetParameterInt("channel", int(texture_channel))
	app.SetParameterInt("parameters.xrad", xrad)
	app.SetParameterInt("parameters.yrad", yrad)
	app.SetParameterString("texture", "simple")
	app.SetParameterString("out", resultspath+texture_map)
	app.ExecuteAndWriteOutput()

	#convert image to use only a subset of the total 8 channels (Haralick texture, Energy, Entropy)
	apptype = "ExtractROI"
	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterString("in", resultspath+texture_map + "?&bands=8,1,2")
	app.SetParameterString("out", resultspath + texture_map_3bands)
	app.ExecuteAndWriteOutput()

#------------------------------------------------------------------------------
	# step 3 Concatenate with input image

	concat_raster_texture = concat_raster_texture.split('.tif')[0] + '_chan_' + str(texture_channel) + '.tif'
	apptype = "ConcatenateImages"
	app = otbApplication.Registry.CreateApplication(apptype)
	#if using all 8 texture bands:
	#app.SetParameterStringList("il", [rimage, resultspath+texture_map])
	#if using the subset (extractROI)
	app.SetParameterStringList("il", [rimage, resultspath + texture_map_3bands])
	app.SetParameterString("out", resultspath + concat_raster_texture)
	app.ExecuteAndWriteOutput()

#------------------------------------------------------------------------------
	#step 4 - train a classifiers with the raster input image and the shapefile with ROIs

	apptype = "TrainImagesClassifier"
	samplemv = 100
	samplemt = 100
	samplevtr = 0.5

	classifier = input_classifier

	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterStringList("io.il", [resultspath + concat_raster_texture])
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
		#color_classified_rimage = b_rimage + tstamp + '_' + jdata['classified_rimage_color_rf']
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
		#color_classified_rimage = b_rimage + tstamp + '_' + jdata['classified_rimage_color_svm']
		con_matrix =  jdata['confusion_matrix_svm']
		app.SetParameterString("classifier.libsvm.k", jdata['svm_k'])
		app.SetParameterFloat("classifier.libsvm.c", float(jdata['svm_c']))
		app.SetParameterString("classifier.libsvm.opt", jdata['svm_opt'])

	app.SetParameterString("io.confmatout", resultspath + con_matrix)
	app.ExecuteAndWriteOutput()

#--------------------------------------------------------------------------------
	#step 5  - classify an input image with the trained model

	apptype = "ImageClassifier"
	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterString("in", rimage)
	app.SetParameterString("model", resultspath + modelname)
	app.SetParameterString("out", resultspath + classified_rimage)
	app.ExecuteAndWriteOutput()

#--------------------------------------------------------------------------------
	#step 6 - calculate classifier statistics

	stats, fname = get_classifier_statistics(location, resultspath, con_matrix, stats_save)
	print('\nHere are the classifier statistics, based on the confusion matrix\n')
	print(stats)
	print('\n')

#--------------------------------------------------------------------------------
	#step 7 - apply colormap

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
			color_classified_rimage = b_rimage + tstamp + '_' + jdata['classified_rimage+texture_color_svm']
		elif(classifier == 'rf'):
			color_classified_rimage = b_rimage + tstamp + '_' + jdata['classified_rimage+texture_color_rf']

		app.SetParameterString("out", resultspath + color_classified_rimage)
		app.ExecuteAndWriteOutput()

#---------------------------------------------------------------------------------
	#step 8 - update settings file with user inputs

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
#---------------------------------------------------------------------------------

	#step 9 - transfer to storage (pCloud)

	if(t2p == "yes"):
		f = open(authfile, 'r')
		lines = f.readlines()
		username = lines[0].strip()
		password = lines[1].strip()
		f.close()

		#zip up the settings and stats (classifier precision, recall and fscore calculated from the confusion matrix)
		st_settings = jdata['stats+settings']
		tstamp = create_timestamp(location)
		stats_settings =  st_settings.split('.zip')[0] + '_' + tstamp + '.zip'
		zipOb = ZipFile(resultspath + stats_settings, 'w')
		zipOb.write(resultspath + fname)
		zipOb.write(inputsfile_updated)			#use the updated file
		zipOb.close()

		conn = PyCloud(username, password, endpoint='nearest')
		if(addcolor == "yes"):
			filelist = [resultspath + color_classified_rimage, resultspath + stats_settings]
		else:
			filelist = [resultspath + classified_rimage, resultspath + stats_settings]

		conn.uploadfile(files=filelist, path=pdir)
		print('\n\nUploaded: ' , filelist)
		print('\n\n')

#---------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------
