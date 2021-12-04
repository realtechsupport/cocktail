# ORFEO Toolbox 
# classifier training and image classification
# install on Ubuntu 18 LTS with conda (conda-packages1.sh and environmentv1.yml.)
# RTS, Nov 2021
# OTB_part2

#sequence
# OTB_part1
# QGIS_join
# OTB_part2
# QGIS_render
# -------------------------------------------------------------
import sys, os, json
from datetime import datetime
import pytz
import gdal
import otbApplication
import numpy 
from PIL import Image as PILImage
#------------------------------------------------------------------------------
# Local path and variables
datapath = '/home/marcbohlen/data/'
inputsfile = datapath + 'inputs.txt'
#collect the variables
try:
        f = open(inputsfile, 'r')
        data = f.read()
        jdata = json.loads(data)
        f.close()
except:
        print('\n...data access error...\n')
else:
	print(jdata)
	rasterimage = jdata['rasterimage']
	pointsfile = jdata['pointsfile']
	classifier_type = jdata['classifier']
	rasterpath = jdata['rasterpath']
	vectorpath = jdata['vectorpath']
	resultspath = jdata['resultspath']
	segmentationfile = jdata['segmentationfile']
	segmentation_stats = jdata['segmentation_stats']
	coord_info = jdata['coord_info']
	segmentation_points_joined = jdata['segmentation_points_joined']
	ann_vector_classification = jdata['ann_vector_classification']
	modelname = jdata['modelname']
	confusion_matrix = jdata['confusion_matrix']
	ann_vector_classification = jdata['ann_vector_classification']

if(classifier_type == 'ann'):
	#TrainVectorClassifiers
	sfile = vectorpath + segmentation_points_joined
	app = otbApplication.Registry.CreateApplication("TrainVectorClassifier")

	print('\n\n Training Neural Network Model\n\n')
	app.SetParameterStringList("io.vd", [sfile])
	app.SetParameterString("io.out", resultspath + modelname)
	
	app.SetParameterStringList("feat", ["mean_0", "stdev_0", "mean_1", "stdev_1", "mean_2", "stdev_2", "mean_3", "stdev_3"])
	app.SetParameterInt("valid.layer", 0) 
	app.SetParameterString("cfield", "class")

	app.SetParameterString("classifier.ann.t", "reg") #reg, back
	app.SetParameterStringList("classifier.ann.sizes", ["10"])
	app.SetParameterString("classifier.ann.f", "sig") #ident, sig, gau
	app.SetParameterFloat("classifier.ann.a", 1.0)
	app.SetParameterFloat("classifier.ann.b", 1.0)
	app.SetParameterFloat("classifier.ann.bpdw", 0.1)
	app.SetParameterFloat("classifier.ann.bpms", 0.1)
	app.SetParameterFloat("classifier.ann.rdw", 0.1)
	app.SetParameterFloat("classifier.ann.rdwm", 1e-07)
	app.SetParameterString("classifier.ann.term", "all")  #iter, eps, all
	app.SetParameterFloat("classifier.ann.eps", 0.01)
	app.SetParameterInt("classifier.ann.iter", 1000)
	app.SetParameterInt("rand", 0)

	app.SetParameterString("io.confmatout", resultspath + confusion_matrix)
	app.ExecuteAndWriteOutput()
	print('\n\nvector train complete... \n\n')

	#step 2  - classify vector file with the trained model
	apptype = "VectorClassifier"
	inputshapefile = segmentation_stats
	sfileout = ann_vector_classification

	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterString("in", vectorpath + inputshapefile)
	app.SetParameterString("model", resultspath + modelname)
	app.SetParameterStringList("feat", ["mean_0", "stdev_0", "mean_1", "stdev_1", "mean_2", "stdev_2", "mean_3", "stdev_3"])
	app.SetParameterString("out", resultspath + sfileout)
	app.ExecuteAndWriteOutput()
	print('\n\nvector classify complete... \n\n')
	#NEXT STEP: QGIS render
	
#--------------------------------------------------------------------------------
