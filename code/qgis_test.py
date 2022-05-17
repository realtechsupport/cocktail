# COCKTAIL
# qgis_test.py
# QGIS test routine - checking the basics
# RTS, October 2021
# https://qgis.org/pyqgis/3.16/index.html
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
	Qgis,
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

print('\nThis is the QGIS version: ', Qgis.QGIS_VERSION)
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
sterm = 'join'
algolist = []
print('\nChecking QGIS for instances of: ', sterm)
for algo in QgsApplication.processingRegistry().algorithms():
	algolist.append(algo.name())
	if(re.search(sterm, algo.name(), re.IGNORECASE)):
		print(algo.name())

print('\n\nHere are all available algorithms in this version of QGIS.')
print(algolist)


#finish
print('\nEnding QGIS')
qgs.exitQgis()

#-----------------------------------------------------------------
