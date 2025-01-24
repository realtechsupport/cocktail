# OpenEO Sentinel-2 data collection
# Dec 2024, RTS
#---------------------------------------------------------------------
import os
import openeo
import json
import numpy
import PIL
import time, random, itertools, shutil

from shapely.geometry import shape
from shapely.ops import unary_union

datapath = "/home/rts/dev/data/" 	# set the data path

from openeo_helper import initialize, create_job
from quality_check import recompile, filter
from utilities import *

#---------------------------------------------------------------------
# set the variables
# London
latitude = 51.5072
longitude = 0.1276

site = str(latitude) + "_" + str(longitude)
savepath = os.path.join(datapath, site) 

# prevent errors on retry with new settings for same location
try:
	os.mkdir(savepath)
except:
	print("Directory already exists.")

satellite = "SENTINEL2_L2A"
max_cloud = 25
start = "2024-12-20"
end = "2025-01-20" 
#band_selection = ["B04", "B03", "B02"] #RGB, TCI
band_selection = ["B08", "B04", "B03", "B02"] #IR R G B

#---------------------------------------------------------------------
bbox = get_coordinates(latitude,longitude,surface_area=100)
print("input bounding box: ", bbox)
#---------------------------------------------------------------------    

# authenticate - auth file has your secrets
print("authenticating...")
f = open('auth.txt', 'r')
data = f.read()
jdata = json.loads(data)
f.close()

copernicus_url = 'openeo.dataspace.copernicus.eu'
connection = openeo.connect(url=copernicus_url)

connection.authenticate_oidc_client_credentials(
    client_id = jdata['client_id'],
    client_secret = jdata['client_secret'],
)
#---------------------------------------------------------------------
print("launching openeo job")
job = create_job(connection, bbox, start, end, satellite, band_selection, max_cloud)
try:
    job.start_and_wait()
except:
    print("something went wrong")
    
#---------------------------------------------------------------------
print("getting results")
try:
	results = job.get_results()
	assets = results.get_assets()

	print("performing early quality check")
	metadata = results.get_metadata()
	compiled = recompile(metadata)
	filtered_images = filter(compiled)
	print(filtered_images)

	print("downloading the filtered results")
	selected_coords = (latitude, longitude)
	download_relevant_files(assets, filtered_images, selected_coords, savepath)

except:
	print("No results available with current settings...")
	exit()


#---------------------------------------------------------------------
