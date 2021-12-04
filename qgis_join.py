# qgis_join.py
# RTS, November 2021
#join attributes by location
#---------------------------------------------------------------------------------------
#sequence
# OTB_part1
# QGIS_join
# OTB_part2
# QGIS_render

import os, sys
import json
import time
import datetime
import os, re

#append the path where processing plugin can be found (assumes Debian OS)
sys.path.append('/usr/share/qgis/python/plugins')

# make sure Qgis does not ask for a screen
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

#indicate the path to qgis
qgispath = '/usr/bin/qgis'

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
	pointsfile = jdata['pointsfile']
	vectorpath = jdata['vectorpath']
	segmentation_stats = jdata['segmentation_stats']
	segmentation_points_joined = jdata['segmentation_points_joined']

#-------------------------------------------------------------
#qgis core module imports
from qgis.core import (QgsApplication)

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

try:
    results = processing.runAndLoadResults(algorithmname, parameters)
    r = results['OUTPUT']
    print('...completed: ', algorithmname)
except e:
    print('something went wrong')


#finish
print('JOIN complete ... ending QGIS')
qgs.exitQgis()

#NEXT STEP: OTB part2 (vector train and test)
#-----------------------------------------------------------------
