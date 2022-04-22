# qgis_bandoperations.py
# RTS, April 2022
# bandmath operations on sentinel2 and landsat spectral bands
#---------------------------------------------------------------------------------------
#sequence
# otb_clip.py > clip all bands to defined shapefile ROI
# qgis_bandoperations > do the band math

import os, sys
import json
import time
import datetime
import os, re

from helper import *

#append the path where processing plugin can be found (assumes Debian OS)
sys.path.append('/usr/share/qgis/python/plugins')

# make sure Qgis does not ask for a screen
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

#indicate the path to qgis
qgispath = '/usr/bin/qgis'

# Local path and variables
datapath = '/home/blc/cocktail/data/'
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
	rasterpath = jdata['rasterpath']
	vectorpath = jdata['vectorpath']
	resultspath = jdata['resultspath']
	collectionpath = jdata['collectionpath']
	sentinelrasterpath = jdata['sentinelrasterpath']
	authfile = jdata['authfile']

	t2p = jdata['T2P']
	pdir = jdata['pdir']
	r_height = int(jdata['r_height'])
	r_width = int(jdata['r_width'])
	background = jdata['background']
	location = jdata['location']

#-------------------------------------------------------------
#qgis core module imports
from qgis.core import (
        QgsApplication,
        QgsProcessingFeedback,
        QgsProcessingException,
        QgsProcessingParameters,
        QgsVectorLayer,
        QgsRasterLayer
)

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

#parameters and inputs
rastershapezipfile =  'area2_0717_2017_sentinel2.zip'
parts = rastershapezipfile.split('_')
token = parts[2] + parts[1]
ext = '.tif'

B11 = findband_roi('B11', token, ext, sentinelrasterpath)
B8A = findband_roi('B8A', token, ext, sentinelrasterpath)

print(B11)
print(B8A)

B11_r = sentinelrasterpath + B11
B8A_r = sentinelrasterpath + B8A

result = resultspath + rastershapezipfile.split('.zip')[0] + ext

algorithmname = "qgis:rastercalculator"
#expression = 

#https://docs.qgis.org/3.22/en/docs/user_manual/processing/console.html?highlight=input
#https://qgis.org/pyqgis/3.4/analysis/QgsRasterCalculator.html
#https://gis.stackexchange.com/questions/218835/raster-calculation-in-qgis-using-python-script
parameters = {
	#'INPUT': B11_r; B8A_r,
	'CELLSIZE' : 0,
	'CRS' : None,
	'EXPRESSION' : (B11_r - B8A_r) / (B11_r + B8A_r),
	'EXTENT' : None,
	#'LAYERS' : ??
	'OUTPUT' : result}

'''
feedback = QgsProcessingFeedback()

try:
	results = processing.run(algorithmname, parameters, feedback=feedback)
	print('...completed: ', algorithmname)
except QgsProcessingException as e:
	print('\n\n ERROR in this operation..')
	print(str(e))
'''
#finish
print('JOIN complete ... ending QGIS')
qgs.exitQgis()

#-----------------------------------------------------------------
