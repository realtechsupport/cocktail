# COCKTAIL
# otb_raster_classify_ni.py
# RTS, March 2022
#---------------------------------------------------------------------------------
# non_interactive version of otb_raster_classify.py for use with
# otb_vary_raster_classify.py
# raster classifier training and image classification
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
#from zipfile import ZipFile

from helper import *

# Local path and variables
datapath = '/home/blc/cocktail/data/'
inputsfile = datapath + 'settings.txt'

#------------------------------------------------------------------------------
def main():
	# print command line arguments
	for arg in sys.argv[1:]:
		print ("\nThis the selected input: ", arg)

	classifier = arg.strip()
	if((classifier == 'libsvm') or (classifier == 'rf')):
		print("Proceeding to vector processing with: ", classifier)
		raster_classify (classifier)
	else:
		print("Only libsvm and rf classifiers supported now... Try again.\n")
		exit()
#------------------------------------------------------------------------------

def raster_classify (classifier):
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

		stats_save = jdata['stats_save']
		t2p = jdata['T2P']
		pdir = jdata['pdir']
		r_height = int(jdata['r_height'])
		r_width = int(jdata['r_width'])
		background = jdata['background']
		location = jdata['location']
		addcolor = jdata['raster_addcolor']


	rimage = rasterpath + rasterimage
	key = "classification"
	s = rastershapezipfile.split(key)
	sf = s[0] + key + ".shp"
	sfile = vectorpath + sf

	print('\nHere are the inputs')
	print('Zipped raster shapefile: ', rastershapezipfile)
	print('Unzipped raster shapefile: ' , sfile)
	print('Rasterimage: ', rasterimage)

	b_rimage = rasterimage.split('.tif')[0] + '_'

#-----------------------------------------------------------------------------
	# step 1 - preparation - copy the selected zipfiles to the vectordata folder and uncompress

	shutil.copy(collectionpath + rastershapezipfile, vectorpath + rastershapezipfile)

	with zipfile.ZipFile(vectorpath + rastershapezipfile, 'r') as zip_ref:
  		zip_ref.extractall(vectorpath)

	print("Selected zipped files moved to vector directory and unzipped..")

#------------------------------------------------------------------------------
	#step 2 - train a classifiers with the raster input image and the shapefile with ROIs

	apptype = "TrainImagesClassifier"
	samplemv = 100
	samplemt = 100
	samplevtr = 0.5

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
		color_classified_rimage = b_rimage + tstamp + '_' + jdata['classified_rimage_color_rf']
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
		color_classified_rimage = b_rimage + tstamp + '_' + jdata['classified_rimage_color_svm']
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

#--------------------------------------------------------------------------------
	#step 5 - apply colormap

	if(addcolor == "yes"):
		print('\n\nApplying colormap\n')
		apptype = "ColorMapping"
		app = otbApplication.Registry.CreateApplication(apptype)
		app.SetParameterString("in", resultspath + classified_rimage)  		#the output of step 2
		app.SetParameterString("method", "custom")
		app.SetParameterString("method.custom.lut", datapath + colortemplate)
		app.SetParameterString("out", resultspath + color_classified_rimage)
		app.ExecuteAndWriteOutput()
#---------------------------------------------------------------------------------
	#step 6 - transfer to storage (pCloud)

	if(t2p == "yes"):
		f = open(authfile, 'r')
		lines = f.readlines()
		username = lines[0].strip()
		password = lines[1].strip()
		f.close()

		#zip up the settings and stats (classifier precision, recall and fscore calculated from the confusion matrix)
		stats_settings = jdata['stats+settings']
		zipOb = ZipFile(resultspath + stats_settings, 'w')
		zipOb.write(resultspath + fname)
		zipOb.write(inputsfile)
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
