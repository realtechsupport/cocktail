# qgis_bandoperations.py
# RTS, April 2022
# bandmath operations on sentinel2 and landsat spectral bands
#---------------------------------------------------------------------------------------
#sequence
# otb_clip.py > clip all bands to defined shapefile ROI
# qgis_bandoperations > do the band math
#--------------------------------------------------------------------------------------

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
#----------------------------------------------------------------------------------------

def main():
	# print command line arguments
	for arg in sys.argv[1:]:
		print ("This the selected input: ", arg)

	type = arg.strip()
	if((type == 'ibi') or (type  == 'nbi') or (type  == 'ui') or (type  == 'ndbi')):
		print("\nProceeding to create change map with: ", type)
		perform_bandoperation(type)
	else:
		print("\nOnly ibi, nbi, ui or ndbi operations possible... Try again.\n")
		exit()
#------------------------------------------------------------------------------
def perform_bandoperation(type):
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


	if(type == 'ui'):
		print("\nUrban Index\n")
		B11 = findband_roi('B11', token, ext, sentinelrasterpath)
		B04 = findband_roi('B04', token, ext, sentinelrasterpath)
		imgA = sentinelrasterpath + B11
		imgB = sentinelrasterpath + B04
		imgC = imgA
		formula = "(A - B) / (A + B)"

	elif(type == 'ndbi'):
		print("\nNormalized Difference Built-Up Index\n")
		B11 = findband_roi('B11', token, ext, sentinelrasterpath)
		B8A = findband_roi('B8A', token, ext, sentinelrasterpath)
		imgA = sentinelrasterpath + B11
		imgB = sentinelrasterpath + B8A
		imgC = imgA
		formula = "(A - B) / (A + B)"


	elif(type == 'nbi'):
		#something wrong here...
		print("\nNew Built-Up Index\n")
		B04 = findband_roi('B04', token, ext, sentinelrasterpath)
		B11 = findband_roi('B11', token, ext, sentinelrasterpath)
		#B08 = findband_roi('B08', token, ext, sentinelrasterpath)
		B8A = findband_roi('B8A', token, ext, sentinelrasterpath)
		imgA = sentinelrasterpath + B04
		imgB = sentinelrasterpath + B11
		imgC = sentinelrasterpath + B8A
		#imgC = sentinelrasterpath + B08
		formula = "(A * B) / C"


	result = resultspath + type + '_' + rastershapezipfile.split('.zip')[0] + ext
	print(result)

	#run the gdal rastercalculator
	algorithmname = "gdal:rastercalculator"
	#https://gis.stackexchange.com/questions/218835/raster-calculation-in-qgis-using-python-script
	#https://gis.stackexchange.com/questions/216851/python-script-for-raster-calculation-using-gdal 
	parameters = {
		'INPUT_A' : imgA,
		'BAND_A' : 1,
		'INPUT_B' : imgB,
		'BAND_B' : 1,
		#'INPUT_C' : imgC,
		#'BAND_C' : 1,
		'FORMULA' : formula,
		'OUTPUT' : result}

	feedback = QgsProcessingFeedback()

	try:
		results = processing.run(algorithmname, parameters, feedback=feedback)
		print('\n...completed: ', algorithmname, type)
	except QgsProcessingException as e:
		print('\n\n ERROR in this operation..')
		print(str(e))

	#finish
	print('...ending QGIS\n')
	qgs.exitQgis()

#---------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------
