# COCKTAIL
# qgis_join.py
# join attributes by location
# vector points shapefile defined in the settings.txt tile
# zipped vector points shapefile expected to end with "final.zip"
# RTS, Feb, Sept 2022

# sequence
# OTB_vector_classify1
# > QGIS_join
# OTB_vector_classify2
# QGIS_render

# -----------------------------------------------------------------------
import os, sys
import json
import time
import datetime
import os, re
#-----------------------------------------------------------------------
print('\nQGIS_JOIN: Join attributes by location\n')
#------------------------------------------------------------------------
#append the path where processing plugin can be found (assumes Debian OS)
sys.path.append('/usr/share/qgis/python/plugins')

# make sure Qgis does not ask for a screen
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

#indicate the path to qgis
qgispath = '/usr/bin/qgis'

# Local path and variables
datapath = '/home/marcbohlen/cocktail/data/'
inputsfile = datapath + 'settings.txt'

#collect the variables
try:
	f = open(inputsfile, 'r')
	data = f.read()
	jdata = json.loads(data)
	f.close()
except:
	print('\n...data access error...\n')
else:
	pointszipfile = jdata['pointszipfile']
	vectorpath = jdata['vectorpath']
	segmentation_stats = jdata['segmentation_stats']
	segmentation_points_joined = jdata['segmentation_points_joined']
	joinmethod = int(jdata['joinmethod'])
	joinprefix = jdata['joinprefix']

#-------------------------------------------------------------
#qgis core module imports
from qgis.core import (
	Qgis,
	QgsApplication,
	QgsProcessingFeedback,
	QgsProcessingException,
	QgsProcessingParameters,
	QgsVectorLayer,
	QgsRasterLayer
)

#import utils
print('\nThis is the qgis version: ', Qgis.QGIS_VERSION)

#start Qgis
print('\nStarting QGIS')
QgsApplication.setPrefixPath(qgispath, True)
qgs = QgsApplication([], False)
qgs.initQgis()

#import additional modules
import processing
from processing.core.Processing import Processing

#start the processing module
processing.core.Processing.Processing.initialize()

#join attributes by location
segmentationstats =  vectorpath + segmentation_stats
key = "final"
s = pointszipfile.split(key)
pointsfile = s[0] + key + ".shp"
print(pointsfile)

samplepoints = vectorpath +  pointsfile
combined = vectorpath + segmentation_points_joined

algorithmname = "qgis:joinattributesbylocation"
parameters = {'INPUT': segmentationstats,
	'JOIN': samplepoints,
	'JOIN_FIELDS': [],
	'METHOD': 1,
	'DISCARD_NONMATCHING': True,
	'PREDICATE': [0],
	'PREFIX': '',
	'OUTPUT' : combined}


feedback = QgsProcessingFeedback()

try:
	results = processing.run(algorithmname, parameters, feedback=feedback)
	print('\nJOIN completed: ', algorithmname)

except QgsProcessingException as e:
	print('\n\n ERROR in this operation..')
	print(str(e))

#finish
print('\nEnding QGIS')
qgs.exitQgis()

#NEXT STEP: OTB part2 (vector train and test)
#-----------------------------------------------------------------
