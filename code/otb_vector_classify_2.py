# COCKTAIL 
# otb_vector_classify_2.py
# classifier training and image classification
# RTS, Feb 2022

# sequence
# OTB_vector_classify1
# QGIS_join
# OTB_vector_clasify2
# QGIS_render

# -----------------------------------------------------------------------------
import sys, os, json
from datetime import datetime
import pytz
import gdal
import otbApplication
import numpy
from PIL import Image as PILImage

#------------------------------------------------------------------------------
print('\nVECTOR_CLASSIFY_2: Training + Classification\n')
#------------------------------------------------------------------------------

# Local path and variables
datapath = '/home/blc/cocktail/data/'
inputsfile = datapath + 'settings.txt'

#collect the variables from the settings file
try:
        f = open(inputsfile, 'r')
        data = f.read()
        jdata = json.loads(data)
        f.close()
except:
        print('\n...data access error...\n')
else:
	rasterimage = jdata['rasterimage']
	pointsfile = jdata['pointsfile']
	classifier = jdata['vector_classifier_ann']
	rasterpath = jdata['rasterpath']
	vectorpath = jdata['vectorpath']
	resultspath = jdata['resultspath']
	segmentationfile = jdata['segmentationfile']
	segmentation_stats = jdata['segmentation_stats']
	coord_info = jdata['coord_info']
	segmentation_points_joined = jdata['segmentation_points_joined']
	cfieldname = jdata['cfieldname']
	NNtraintype = jdata['NNtraintype']
	NNsize = jdata['NNsize']	#10 or 10, 10 (one or two hidden layers)
	NNactivation = jdata['NNactivation']
	NNalpha = float(jdata['NNalpha'])
	NNbeta = float(jdata['NNbeta'])
	NNbackpropweightgradient = float(jdata['NNbackpropweightgradient'])
	NNmomentum = float(jdata['NNmomentum'])
	NNinitialdelta = float(jdata['NNinitialdelta'])
	NNupdatedelta = float(jdata['NNupdatedelta'])
	NNterminationcriteria = jdata['NNterminationcriteria']
	NNepsilon = float(jdata['NNepsilon'])
	NNmaxiterations = int(jdata['NNmaxiterations'])
#------------------------------------------------------------------------------

if(classifier == 'ann'):
	#TrainVectorClassifiers
	sfile = vectorpath + segmentation_points_joined
	app = otbApplication.Registry.CreateApplication("TrainVectorClassifier")
	modelname = jdata['modelname_vector_ann']
	confusion_matrix = jdata['confusion_matrix_vector_ann']
	ann_vector_classification = jdata['ann_vector_classification']

	mean_std_list = ["mean_0", "stdev_0", "mean_1", "stdev_1", "mean_2", "stdev_2", "mean_3", "stdev_3"]
	app.SetParameterStringList("io.vd", [sfile])
	app.SetParameterString("io.out", resultspath + modelname)

	app.SetParameterStringList("feat", mean_std_list)
	app.SetParameterInt("valid.layer", 0)

	app.SetParameterString("cfield", cfieldname)
	app.SetParameterString("classifier.ann.t", NNtraintype) 		#reg, back
	app.SetParameterStringList("classifier.ann.sizes", [NNsize])		#10 or 10, 10 (one or two hidden layers)
	app.SetParameterString("classifier.ann.f", NNactivation) 		#ident, sig, gau
	app.SetParameterFloat("classifier.ann.a", NNalpha)
	app.SetParameterFloat("classifier.ann.b", NNbeta)
	app.SetParameterFloat("classifier.ann.bpdw", NNbackpropweightgradient)
	app.SetParameterFloat("classifier.ann.bpms", NNmomentum)
	app.SetParameterFloat("classifier.ann.rdw", NNinitialdelta)
	app.SetParameterFloat("classifier.ann.rdwm", NNupdatedelta)
	app.SetParameterString("classifier.ann.term", NNterminationcriteria)	#iter, eps, all
	app.SetParameterFloat("classifier.ann.eps", NNepsilon)
	app.SetParameterInt("classifier.ann.iter", NNmaxiterations)


	print('\n\nTraining Neural Network Model')
	app.SetParameterInt("rand", 0)
	app.SetParameterString("io.confmatout", resultspath + confusion_matrix)
	app.ExecuteAndWriteOutput()
	print('\n\nVector training complete.')

	#step 2  - classify vector file with the trained model
	apptype = "VectorClassifier"
	inputshapefile = segmentation_stats
	sfileout = ann_vector_classification

	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterString("in", vectorpath + inputshapefile)
	app.SetParameterString("model", resultspath + modelname)
	app.SetParameterStringList("feat", mean_std_list)
	app.SetParameterString("out", resultspath + sfileout)
	app.ExecuteAndWriteOutput()
	print('\n\nVector classify complete.')

	#NEXT STEP: QGIS render

#--------------------------------------------------------------------------------
