# qgis_basics.py
# QGIS test routine - checking the basics
# RTS, October 2021
# https://docs.qgis.org/3.16/en/docs/pyqgis_developer_cookbook/loadlayer.html
# https://qgis.org/pyqgis/3.16/index.html
# --------------------------------------------------------------------------
# place all the shape file data (.shp, shx, dbf,.prj, .qix) into one folder
#--------------------------------------------------------------------------
import sys
import time
import datetime
import os, re

#append the path where processing plugin can be found (assumes Debian OS)
sys.path.append('/usr/share/qgis/python/plugins')

# make sure Qgis does not ask for a screen
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

#indicate the path to qgis
qgispath = '/usr/bin/qgis'

#qgis core module imports
from qgis.core import (
	QgsApplication,
	QgsProcessingFeedback,
	QgsVectorLayer,
	QgsRasterLayer,
	QgsField,
	QgsFields,
	QgsProject,
	QgsProperty,
	QgsProcessingFeatureSourceDefinition,
	QgsProcessingOutputLayerDefinition
)
#----------------------------------------------------------------------------

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

#search available algorithms for a specific item
sterm = 'nearest'
for algo in QgsApplication.processingRegistry().algorithms():
	if(re.search(sterm, algo.name(), re.IGNORECASE)):
		print(algo.name())

#finish
print('\nEnding QGIS')
qgs.exitQgis()

#-----------------------------------------------------------------
