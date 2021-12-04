# qgis_remder.py
# RTS, November 2021
# render vector classification with a .qml color map
#---------------------------------------------------------------------------------------
#sequence
# OTB_part1
# QGIS_join
# OTB_part2
# QGIS_render

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
inputsfile = datapath + 'inputs.txt'

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
	colortemplate = jdata['colortemplate']
	classified_vimage = jdata['classified_vimage']
	pdir = jdata['pdir']
	r_height = int(jdata['r_height'])
	r_width = int(jdata['r_width'])
	background = jdata['background']

#output from OTB_part2
shapefile = resultspath + ann_vector_classification

#add timestamp to classified vimage
rastername = rasterimage.split('.tif')[0]
classified_vimage = rastername + '_' + classified_vimage + '_' + classifier + '.png'

T2P = True

#-------------------------------------------------------------------------------
#qgis core module imports
from qgis.core import (
    QgsApplication, 
    QgsPrintLayout,
    QgsMapSettings,
    QgsMapRendererParallelJob,
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

from qgis.PyQt.QtCore import (
    QPointF,
    QRectF,
    QSize,
)
#------------------------------------------------------------------------------
#start Qgis
print('\nStarting QGIS')
QgsApplication.setPrefixPath(qgispath, True)
qgs = QgsApplication([], False)
qgs.initQgis()

#import additional modules
import processing
from processing.core.Processing import Processing
processing.core.Processing.Processing.initialize()
from processing.tools import *

#write the features of the vector layer to a file
vlayer = QgsVectorLayer(shapefile, "temp", "ogr")

if not vlayer.isValid():
	print("Vector data failed to load!\n")
else:
	print('vector data loaded...\n')

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
render.start()

# loop for a standalone example.
from qgis.PyQt.QtCore import QEventLoop
loop = QEventLoop()
render.finished.connect(loop.quit)
loop.exec_()

#finish
print('\nEnding QGIS')
qgs.exitQgis()

#-----------------------------------------------------------

if(T2P):
	f = open(authfile, 'r')
	lines = f.readlines()
	username = lines[0].strip()
	password = lines[1].strip()
	f.close()
	try:	
		conn = PyCloud(username, password, endpoint='nearest')
		filelist = [resultspath + classified_vimage]
		conn.uploadfile(files=filelist, path=pdir)
		print('\n\nUploaded: ' , filelist)
	except:
		print('\npCloud error...upload failed..')
		pass
else:
	print('\n...not uploading to pCloud...\n')
#-----------------------------------------------------------
