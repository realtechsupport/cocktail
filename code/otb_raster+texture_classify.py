# ORFEO Toolbox
# raster classifier training and image classification
# ------------------------------------------------------------------------------
# Combine with texture map that produces an output with the following texture measures:
# 1-Energy, 2-Entropy, 3-Correlation, 4-Inverse Difference Moment, 5-Inertia, 6-Cluster Shade, 7-Cluster Prominence, 8-Haralick Correlation
# http://wiki.awf.forst.uni-goettingen.de/wiki/index.php/Haralick_Texture
# Concatenate
# Then classify: classifiers: Support Vector Machine, Random Forest
# Check variation in LIBSVM
# https://www.orfeo-toolbox.org/CookBook/Applications/app_TrainImagesClassifier.html?highlight=libsvm

# Add color map
# Transport to pCloud
# install on Ubuntu 18 LTS with conda (conda-packages1.sh and environmentv1.yml.)
# RTS, Nov/Dec 2021
# updated with classifier statistics, Jan 2022
# updated with texture, Feb 2022
# ------------------------------------------------------------------------------
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

	classifier = arg.strip()
	if((classifier == 'libsvm') or (classifier == 'rf')):
		print("\nProceeding to vector processing with ", classifier)
		raster_texture_classify (classifier)
	else:
		print("\nOnly libsvm and rf classifiers supported now... Try again.\n")
		exit()
#------------------------------------------------------------------------------
def raster_texture_classify (classifier):
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
		rastershapefile = jdata['rastershapefile']
		rasterpath = jdata['rasterpath']
		vectorpath = jdata['vectorpath']
		resultspath = jdata['resultspath']
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

	rimage = rasterpath + rasterimage
	sfile = vectorpath +  rastershapefile
	print('\nHere are the inputs')
	print('Shapefile: ', sfile)
	print('Rasterimage: ', rasterimage)
	print('\n')
	b_rimage = rasterimage.split('.tif')[0] + '_'

#------------------------------------------------------------------------------
	# step 1: get texture information (missing select only bands 8,3,1 ....)

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
	# step 2 Concatenate with input image

	concat_raster_texture = concat_raster_texture.split('.tif')[0] + '_chan_' + str(texture_channel) + '.tif'
	apptype = "ConcatenateImages"
	app = otbApplication.Registry.CreateApplication(apptype)
	#if using all 8 texture bands:
	#app.SetParameterStringList("il", [rimage, resultspath+texture_map])
	#if using the subset (extractROI)
	app.SetParameterStringList("il", [rimage, resultspath + texture_map_3bands])
	app.SetParameterString("out", resultspath + concat_raster_texture)
	app.ExecuteAndWriteOutput()

	#step 3 - train a classifiers with the raster input image and the shapefile with ROIs

	apptype = "TrainImagesClassifier"
	samplemv = 100
	samplemt = 100
	samplevtr = 0.5

	app = otbApplication.Registry.CreateApplication(apptype)
	#app.SetParameterStringList("io.il", [rimage])
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
		app.SetParameterFloat("classifier.libsvm.c", int(jdata['svm_c']))
		app.SetParameterString("classifier.libsvm.opt", jdata['svm_opt'])

	app.SetParameterString("io.confmatout", resultspath + con_matrix)
	app.ExecuteAndWriteOutput()

#--------------------------------------------------------------------------------
	#step 4  - classify an input image with the trained model

	apptype = "ImageClassifier"
	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterString("in", rimage)
	app.SetParameterString("model", resultspath + modelname)
	app.SetParameterString("out", resultspath + classified_rimage)
	app.ExecuteAndWriteOutput()

#--------------------------------------------------------------------------------
	#step 5 - calculate classifier statistics

	stats, fname = get_classifier_statistics(resultspath, con_matrix, stats_save)
	print('\nHere are the classifier statistics, based on the confusion matrix\n')
	print(stats)
	print('\n')

#--------------------------------------------------------------------------------
	#step 6 - apply colormap

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
	#step 7 - transfer to storage (pCloud)

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
