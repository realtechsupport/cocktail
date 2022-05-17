# COCKTAIL
# qgis_render.py
# select dissolve and then render vector classification with a .qml color map
# RTS, March 2022

# sequence
# OTB_vector_classify1
# QGIS_join
# OTB__vector_classify2
# QGIS_render

#---------------------------------------------------------------------------------------
import os, sys, json
from datetime import datetime
import pytz
from zipfile import ZipFile
from pcloud import PyCloud

from helper import *

#---------------------------------------------------------------------------------------
print('\nQGIS_RENDER: Dissolve boundaries and apply custom color map\n')
#---------------------------------------------------------------------------------------

# tiny helper function here...
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
datapath = '/home/blc/cocktail/data/'
inputsfile = datapath + 'settings.txt'

try:
        f = open(inputsfile, 'r')
        data = f.read()
        jdata = json.loads(data)
        f.close()
except:
        print('\n...data access error...\n')
else:
	rasterimage = jdata['rasterimage']
	vectorpath = jdata['vectorpath']
	resultspath = jdata['resultspath']
	classifier = jdata['vector_classifier_ann']
	authfile = jdata['authfile']
	location = jdata['location']
	ann_vector_classification = jdata['ann_vector_classification']
	colortemplate = jdata['colortemplate_qgis']
	classified_vimage = jdata['classified_vimage']

	perform_dissolve = jdata['perform_dissolve']
	do_zip = jdata['do_zip']
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

	con_matrix = jdata["confusion_matrix_vector_ann"]
	stats_save = jdata['stats_save']
	t2p = jdata['T2P']
	pdir = jdata['pdir']
	r_height = int(jdata['r_height'])
	r_width = int(jdata['r_width'])
	background = jdata['background']
	add_shps = jdata['add_result_shapefiles']

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

tstamp = create_timestamp(location)

if(perform_dissolve == "yes"):
	#dissolve the layer ----------------------------------------------------
	classified_vimage = rastername + '_' + tstamp + '_' + classified_vimage + '_' + classifier + '_dissolved.png'
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
	classified_vimage = rastername + '_' + tstamp + '_' + classified_vimage + '_' + classifier + '.png'
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

#----------------------------------------------------------------------------------
#get classifier statistics
stats, fname = get_classifier_statistics(location, resultspath, con_matrix, stats_save)
print('\nHere are the classifier statistics, based on the confusion matrix\n')
print(stats)
print('\n')

#----------------------------------------------------------------------------------
#collect elements of the resultant shapefile
if((do_zip == "yes") and (perform_dissolve == "yes")):
	base = dissolved_shapefile.split('.shp')[0]
	ziped =  jdata['ziped']
	zipOb = ZipFile(resultspath + ziped , 'w')
	zipOb.write(base + '.shp')
	zipOb.write(base + '.shx')
	zipOb.write(base + '.prj')
	zipOb.write(base + '.dbf')
	zipOb.close()
	print('\nResult shapefiles compressed..')

#-----------------------------------------------------------------------------------
#step 6 - transfer to storage (pCloud)

if(t2p == "yes"):

	stats_settings = jdata['stats+settings']
	stats_settings_tstamp = stats_settings.split('.zip')[0] + '_' + tstamp + '.zip'
	zipOb = ZipFile(resultspath + stats_settings_tstamp, 'w')
	zipOb.write(resultspath + fname)
	zipOb.write(inputsfile)
	zipOb.close()

	filelist = [resultspath + classified_vimage, resultspath + ziped, resultspath + stats_settings_tstamp]
	send_to_pcloud(filelist, authfile, pdir)

else:
	print('\nNot uploading result...\n')

#----------------------------------------------------------------------------------
