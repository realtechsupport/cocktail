# ORFEO Toolbox 
# raster classifier training and image classification
# classifiers: Support Vector Machine, Random Forest, Artificial Neural Net
# color map
# transport to pCloud
# install on Ubuntu 18 LTS with conda (conda-packages1.sh and environmentv1.yml.)
# RTS, Nov 2021
# -------------------------------------------------------------
import sys, os
import json
from datetime import datetime
import pytz
import gdal
import otbApplication
import numpy
from PIL import Image as PILImage
from pcloud import PyCloud

#------------------------------------------------------------------------------
def create_timestamp(location):
    tz = pytz.timezone(location)
    now = datetime.now(tz)
    current_time = now.strftime("%d-%m-%Y-%H-%M")
    return(current_time) 

#------------------------------------------------------------------------------
# Local path and variables
datapath = '/home/marcbohlen/data/'
inputsfile = datapath + 'settings.txt'
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

	t2p = jdata['T2P']
	pdir = jdata['pdir']
	r_height = int(jdata['r_height'])
	r_width = int(jdata['r_width'])
	background = jdata['background']
	location = jdata['location']
	addcolor = jdata['raster_addcolor']

rimage = rasterpath + rasterimage
sfile = vectorpath +  rastershapefile
b_rimage = rasterimage.split('.tif')[0] + '_'

#------------------------------------------------------------------------------
#step 1 - train a classifiers with the raster input image and the shapefile with ROIs
classifier = jdata['raster_classifier_svm']	#rf, libsvm, ann



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
	app.SetParameterFloat("classifier.libsvm.c", int(jdata['svm_c']))
	app.SetParameterString("classifier.libsvm.opt", jdata['svm_opt'])


'''
#TODO .....
#Neural Net
elif(classifier == 'ann'):
	NNtraintype = jdata['NNtraintype']
        NNsize = jdata['NNsize']        #10 or 10, 10 (one or two hidden layers)
        NNactivation = jdata['NNactivation']
        NNalpha = float(jdata['NNalpha'])
        NNbeta = float(jdata['NNbeta'])
        NNbackpropweightgradient = float(jdata['NNbackpropweightgradient'])
        NNmomentum = float(jdata['NNmomentum'])
	
	print('\n\n Training Neural Network Model\n\n')
	modelname = 'model_nn.txt'
	app.SetParameterString("io.out", resultspath + modelname)
	classified_rimage = b_rimage + tstamp + '_classified_nn.tif'
	color_classified_rimage = b_rimage + tstamp + '_color_classified_nn.png'
	con_matrix = 'confusionmatrix_nn.csv'
	app.SetParameterString("classifier.ann.t", "back") #reg, back
	app.SetParameterStringList("classifier.ann.sizes", ["6"])
	app.SetParameterString("classifier.ann.f", "gau") #ident, sig, gau
	app.SetParameterFloat("classifier.ann.a", 1.0)
	app.SetParameterFloat("classifier.ann.b", 1.0)
	app.SetParameterFloat("classifier.ann.bpdw", 0.1)
	app.SetParameterFloat("classifier.ann.bpms", 0.1)
	app.SetParameterFloat("classifier.ann.rdw", 0.1)
	app.SetParameterFloat("classifier.ann.rdwm", 1e-07)
	app.SetParameterString("classifier.ann.term", "all")  #iter, eps, all
	app.SetParameterFloat("classifier.ann.eps", 0.01)
	app.SetParameterInt("classifier.ann.iter", 5000)
'''

app.SetParameterString("io.confmatout", resultspath + con_matrix)
app.ExecuteAndWriteOutput()

#--------------------------------------------------------------------------------
#step 2  - classify an input image with the trained model

apptype = "ImageClassifier"
app = otbApplication.Registry.CreateApplication(apptype)
app.SetParameterString("in", rimage)
app.SetParameterString("model", resultspath + modelname)
app.SetParameterString("out", resultspath + classified_rimage)
app.ExecuteAndWriteOutput()

#--------------------------------------------------------------------------------
if(addcolor == "yes"):
	print('\n\nApplying colormap\n\n')
	apptype = "ColorMapping"
	app = otbApplication.Registry.CreateApplication(apptype)
	app.SetParameterString("in", resultspath + classified_rimage)  		#the output of step 2
	app.SetParameterString("method", "custom")
	app.SetParameterString("method.custom.lut", datapath + colortemplate)
	app.SetParameterString("out", resultspath + color_classified_rimage)
	app.ExecuteAndWriteOutput()
#---------------------------------------------------------------------------------

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
