# COCKTAIL
# otb_raster_train.py
# RTS, October 2022
#---------------------------------------------------------------------------------
# raster classifier training with one or multiple pairs of raster images and
# corresponding shapefiles, resulting in one model
# classifiers: Support Vector Machine, Random Forest
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

	print('\nYou can use this routine to train a classifier on PlanetLab, Sentinel2 or Landsat8 data')
	print('The raster images and shapefiles should be in the collection directory.')
	print('Supported classification options are: rf (RandomForests) or libsvm (SupportVectorMachine)')
	print('Enter the name of the first raster image, with the correspoding the shape file [no comma].')
	print('Select at least one set, max number of pairs is 3.')
	print('After you entered all pairs, enter the classifier.')
	print('Example: ')
	print('area2_0612_2020_4bands.tif area2_0612_2020_raster_classification_4band_final.zip')
	print('area2_0612_2021_4bands.tif area2_0612_2021_raster_classification_4band_final.zip')
	print('rf')
	print('\nThe resultant model will be saved to the results directory and uploaded to storage, if enabled.\n')

	response = 'na'
	paircount = 0;
	pairlimit = 3;
	responses = []
	cls = ['rf', 'libsvm']
	input_classifier = 'na'
	input_rasterimages = []
	input_shapefiles = []

	while ((response not in cls) and (paircount < (pairlimit+1))):
		response = input("Enter the raster image and corresponding shapefile or end with the classifier: ")
		responses.append(response)
	try:
		for entry in responses:
			elements = entry.split(' ')
			if(len(elements) > 1):
				raster = elements[0]
				shapefile = elements[1]
				input_rasterimages.append(raster)
				input_shapefiles.append(shapefile)
			elif(len(elements) == 1):
				classifier = elements[0]

		input_classifier = classifier

	except:
		print('Error on input... try again')
		exit()

	raster_train(input_rasterimages, input_shapefiles, input_classifier)

#---------------------------------------------------------------------------------
def raster_train (input_rasterimages, input_shapefiles, input_classifier):
	try:
        	f = open(inputsfile, 'r')
        	data = f.read()
        	jdata = json.loads(data)
        	f.close()
	except:
        	print('\n...data access error...\n')
	else:
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

	rasterimages = []
	shapefiles = []
	key = ".zip"
	nr = 0; ns = 0;
	for entry in input_rasterimages:
		rasterimages.append(rasterpath + entry)
		nr = nr + 1 ;
	for entry in input_shapefiles:
		s = entry.split(key)
		sf = s[0] + ".shp"
		shapefiles.append(vectorpath + sf)
		ns = ns + 1;
	print('Rasterimages: ', rasterimages)
	print('Shapefiles: ', shapefiles)
	print('Classifier: ', input_classifier)
	print('Number of rasters and number of shapefiles: ', nr, ns)

#-----------------------------------------------------------------------------
	# step 1 - preparation
	print('Moving data from collection to the vectorfiles and rasterimages...')

	#check number of raster images and shapefiles
	if((ns == nr) and (nr > 0)):
		for i in range(nr):
			print('Working on raster - shapefile pair: ', i)
			try:
				shutil.copy(collectionpath +  input_rasterimages[i], rasterpath + input_rasterimages[i])
			except:
				print('\nCant find the raster image... Try again...')
				exit()

			try:
				shutil.copy(collectionpath + input_shapefiles[i], vectorpath + input_shapefiles[i])
			except:
				print('\nCant find the vector data ... Check settings...')
				exit()

			with zipfile.ZipFile(vectorpath + input_shapefiles[i], 'r') as zip_ref:
  				zip_ref.extractall(vectorpath)
			
			print('Raster and shapefile pair prepared.')
	else:
		print('Raster images not paired with shapefiles.. check inputs.')
		exit()

#------------------------------------------------------------------------------
	#step 2 - train a classifiers with the raster input image and the shapefile with ROIs

	apptype = "TrainImagesClassifier"
	samplemv = 100
	samplemt = 100
	samplevtr = 0.5

	classifier = input_classifier
	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterStringList("io.il", rasterimages)
	app.SetParameterStringList("io.vd", shapefiles)

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
		con_matrix =  jdata['confusion_matrix_svm']
		app.SetParameterString("classifier.libsvm.k", jdata['svm_k'])
		app.SetParameterFloat("classifier.libsvm.c", float(jdata['svm_c']))
		app.SetParameterString("classifier.libsvm.opt", jdata['svm_opt'])

	app.SetParameterString("io.confmatout", resultspath + con_matrix)
	app.ExecuteAndWriteOutput()
	print('\n\nModel created and saved...\n')

#--------------------------------------------------------------------------------

	#step 3 - calculate classifier statistics

	stats, fname = get_classifier_statistics(location, resultspath, con_matrix, stats_save)
	print('\nHere are the classifier statistics, based on the confusion matrix\n')
	print(stats)
	print('\n')

#--------------------------------------------------------------------------------

	#step 4 - update settings file with user inputs
	#I am only updating the first pair of raster + shapefile.
	imagetoken = jdata['input_rasterimage']
	classifiertoken = jdata['input_classifier']
	shapefiletoken = rastershapezipfile
	#read in the data from the settings file
	try:
		f = open(inputsfile, 'r')
		data = f.readlines()
		c = 0
		iline = 0
		cline = 0
		sline = 0

		for line in data:
			if(imagetoken in line):
				imagereplacement = line.replace(imagetoken, rasterimages[0])
				iline = c
				#print(imagereplacement)
			elif(classifiertoken in line):
				classificationreplacement = line.replace(classifiertoken, input_classifier)
				cline = c
				#print(classificationreplacement)
			elif(shapefiletoken in line):
				shapefilereplacement = line.replace(shapefiletoken, shapefiles[0])
				sline = c
				#print(shapefilereplacement)
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
			elif(cc == sline):
				f.write(shapefilereplacement)
			else:
				f.write(line)
			cc = cc+1
		f.close()
		print('\nUpdated settings file saved...\n')

	except:
		print('Updated settings file error...')
		exit()

#-------------------------------------------------------------------------------

	#step 5 - transfer to model and settings to storage (pCloud)

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
		#add confusion matrix
		zipOb.write(resultspath + con_matrix)
		zipOb.write(inputsfile)
		zipOb.close()

		conn = PyCloud(username, password, endpoint='nearest')
		filelist = [resultspath + modelname, resultspath + stats_settings_tstamp]

		conn.uploadfile(files=filelist, path=pdir)
		print('\n\nUploaded: ' , filelist)
		print('\n\n')
#---------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------
