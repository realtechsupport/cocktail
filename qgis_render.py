# qgis_remder.py
# RTS, December 2021
# select dissolve and then render vector classification with a .qml color map
#---------------------------------------------------------------------------------------
#sequence
# OTB_part1
# QGIS_join
# OTB_part2
# QGIS_render

import sys
#clear all variables (from last session)
#sys.modules[__name__].__dict__.clear()

import os, sys, json
from datetime import datetime
import pytz
from pcloud import PyCloud

#---------------------------------------------------------------------------------------
def create_timestamp(location):
    tz = pytz.timezone(location)
    now = datetime.now(tz)
    current_time = now.strftime("%d-%m-%Y-%H-%M")
    return(current_time) 

def finished():
    img = render.renderedImage()
    img.save(image_location, "png")
#---------------------------------------------------------------------------------------

#append the path where processing plugin can be found (assumes Debian OS)
sys.path.append('/usr/share/qgis/python/plugins')

# make sure Qgis does not ask for a screen
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

#indicate the path to qgis
qgispath = '/usr/bin/qgis'

#---------------------------------------------------------------------------------------
#collect the variables
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
	rasterimage = jdata['rasterimage']
	vectorpath = jdata['vectorpath']
	resultspath = jdata['resultspath']
	classifier = jdata['classifier']
	authfile = jdata['authfile']
	location = jdata['location']
	ann_vector_classification = jdata['ann_vector_classification']
	colortemplate = jdata['colortemplate_qgis']
	classified_vimage = jdata['classified_vimage']

	perform_dissolve = jdata['perform_dissolve']
	dissolved_shapefile = jdata['dissolved_shapefile']
	compute_area = jdata['COMPUTE_AREA']
	compute_statistics = jdata['COMPUTE_STATISTICS']
	count_features = jdata['COUNT_FEATURES']
	explode_collections = jdata['EXPLODE_COLLECTIONS']
	ref_field = jdata['FIELD']
	geometry = jdata['GEOMETRY']
	keep_attributes = jdata['KEEP_ATTRIBUTES']
	options = jdata['OPTIONS']
	statistics_attribute = jdata['STATISTICS_ATTRIBUTE']

	t2p = jdata['T2P']
	pdir = jdata['pdir']
	r_height = int(jdata['r_height'])
	r_width = int(jdata['r_width'])
	background = jdata['background']

#output from OTB_part2
render_shapefile = resultspath + ann_vector_classification

#create the final image name
rastername = rasterimage.split('.tif')[0]

#-------------------------------------------------------------------------------
#qgis core module imports
from qgis.core import (
	QgsApplication, 
	QgsPrintLayout,
	QgsMapSettings,
	QgsMapRendererParallelJob,
	QgsProcessingFeedback, 
	QgsProcessingException,
	QgsProcessingParameters,
	QgsVectorLayer,
	QgsRasterLayer,
	QgsField,
	QgsFields,
	QgsProcessingFeatureSourceDefinition,
	QgsProcessingOutputLayerDefinition,
	QgsProject,
	QgsProperty
)
from qgis.PyQt.QtCore import (
	QPointF,
	QRectF,
	QSize,
)
#------------------------------------------------------------------------------
#start Qgis
print('\nStarting QGIS for render stage')
QgsApplication.setPrefixPath(qgispath, True)
qgs = QgsApplication([], False)
qgs.initQgis()

#import additional modules
import processing
from processing.core.Processing import Processing
processing.core.Processing.Processing.initialize()
from processing.tools import *

if(perform_dissolve == "yes"):
	#dissolve the layer ----------------------------------------------------------------------
	classified_vimage = rastername + '_' + classified_vimage + '_' + classifier + '_dissolved.png'
	dissolved_shapefile =  resultspath + dissolved_shapefile
	algorithmname = "gdal:dissolve"
	print('\n\nRunning GDAL dissolve ...this step takes about 20 minutes [16GB RAM]\n')

	parameters = {
		'INPUT': render_shapefile,
		'COMPUTE_AREA' : compute_area,
		'COMPUTE_STATISTICS' : compute_statistics,
		'COUNT_FEATURES' : count_features,
		'EXPLODE_COLLECTIONS' : explode_collections,
		'FIELD' : ref_field, 
		'GEOMETRY' : geometry,
		'KEEP_ATTRIBUTES' : keep_attributes,
		'OPTIONS' : options,
		'STATISTICS_ATTRIBUTE' : statistics_attribute,
		'OUTPUT' : dissolved_shapefile}

	feedback = QgsProcessingFeedback()

	try:
		results = processing.run(algorithmname, parameters, feedback=feedback)
		working_shapefile = dissolved_shapefile
		print('...completed: ', algorithmname)

	except QgsProcessingException as e:
		print('\n\nERROR in this operation..')
		print(str(e))

else:
	print('\n\nNot performing the dissolve operation...')
	classified_vimage = rastername + '_' + classified_vimage + '_' + classifier + '.png'
	working_shapefile = render_shapefile

#--------------------------------------------------------------------------------------
#write the features of the vector layer to a file
vlayer = QgsVectorLayer(working_shapefile, "temp", "ogr")
if not vlayer.isValid():
	print("Vector data failed to load!\n")
else:
	print("Vector data loaded...\n")

#add color template
vlayer.loadNamedStyle(datapath + colortemplate)
    
#render the results (from the layer file)
image_location = resultspath + classified_vimage

#do the settings
settings = QgsMapSettings()
settings.setLayers([vlayer])
settings.setOutputSize(QSize(r_height, r_width))
settings.setExtent(vlayer.extent())

#set the renderer
render = QgsMapRendererParallelJob(settings)
render.finished.connect(finished)

# start the rendering
print('\nPerforming the render operation\n')
render.start()

# loop for a standalone example.
from qgis.PyQt.QtCore import QEventLoop
loop = QEventLoop()
render.finished.connect(loop.quit)
loop.exec_()

#finish
print('\nRender complete; ending QGIS')
qgs.exitQgis()

#-----------------------------------------------------------

if(t2p == "yes"):
	f = open(authfile, 'r')
	lines = f.readlines()
	username = lines[0].strip()
	password = lines[1].strip()
	f.close()
	try:
		conn = PyCloud(username, password, endpoint='nearest')
		filelist = [resultspath + classified_vimage]
		conn.uploadfile(files=filelist, path=pdir)
		print('\n\nUploading to remote storage: ' , filelist)
	except:
		print('\npCloud error...upload failed..')
		pass
else:
	print('\nNot uploading result...\n')
#-----------------------------------------------------------
