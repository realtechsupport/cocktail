# COCKTAIL
# planet_get_preview.py
# get thumbmnail size perviews of a scene based on AOI, date and cloudcover
#--------------------------------------------------------------------------------------------
# You need a valid planet lab API key to use this routine
# Place the key in the auth folder (or modify the code to your liking)
# planet API V1

# Usage: -------------------------------------------------------------------------------------
# > python3 planet_get_preview.py
#
# Enter choices at the prompt
# inputs: geojson, target date, max cloudcover
# Make sure the selected geojson map is saved to the data folder

# Updated for SuperDove
# https://tinyurl.com/superdoved
# https://tinyurl.com/superdove8bands
# https://tinyurl.com/355cz2kc

# Asset requests after May 2022 will fetch SuperDove 8-band data.
# Asset requests before that data get Dove 4-band data.
#-------------------------------------------------------------------------------
import sys, os
import json, requests
from requests.auth import HTTPBasicAuth
from planet_helper import *
from pcloud import PyCloud

# Local path and variables
datapath = '/home/marcbohlen/cocktail/data/'
inputsfile = datapath + 'settings.txt'

#----------------------------------------------------------------------------------------------
def main():

	elements = []
	print('Use this routine to get a planet lab satellite asset if you have a vali API key.')
	print('\nEnter the name of the geojson file, target date and max cloud cover.')
	print('Enter the date in year-month-day (2021-05-12) format and cloud cover as a percentage (25).')
	print('Example: area2_square.geojson 2022-08-01 25 {space separated}')
	print('if you do not enter any choices, default values from the settings.txt file will be used.')

	response = input("\nEnter your choices: ")
	try:
		elements = response.split(' ')
		map_geojson = elements[0]
		ptargetdate = elements[1]
		maxcloud = elements[2]
	except:
		map_geojson = 'na'
		ptargetdate = 'na'
		maxcloud = 'na'
		print('\nInput is empty - using defaults from settings file')

	get_planet_data_v1(map_geojson, ptargetdate, maxcloud)

#----------------------------------------------------------------------------------------------
def get_planet_data_v1(map_geojson, ptargetdate, maxcloud):

	try:
        	f = open(inputsfile, 'r')
        	data = f.read()
        	jdata = json.loads(data)
        	f.close()
	except:
        	print('\n...data access error...check settings.txt\n')

	else:
		collectionpath = jdata['collectionpath']
		rasterpath = jdata['rasterpath']
		planetrasterpath = jdata['planetrasterpath']
		planetpreviewpath = jdata['planetpreviewpath']
		rawsatpath = jdata['rawsatpath']
		authfile = jdata['authfile']
		planetauthfile = jdata['planetauthfile']
		location = jdata['location']
		pcloudpreviewdir = jdata['pcloudpreviewdir']
		t2p = jdata['T2P']
		roi = jdata['roi']
		roipath = jdata['roipath']

	if(map_geojson == 'na'):
		map = jdata['geojsonmap']
	else:
		map = map_geojson


	if(maxcloud == 'na'):
		maxcloudcover = jdata['maxcloudcover']
	else:
		maxcloudcover = maxcloud


	if(ptargetdate == 'na'):
		targetdate = jdata['planet_targetdate']
	else:
		targetdate = ptargetdate

	print('\nUsing these settings: ' , map, targetdate, maxcloudcover)

	# --------------------------------------------------------------------------

	start = targetdate
	#prevent date format snafu ..
	try:
		info = targetdate.split('-')
	except:
		info = targetdate.split('_')

	day = info[2]
	month = info[1]
	year = info[0]
	end_day = str(int(day) + 1).zfill(2)
	end = info[0] + '-' + info[1] + '-' + end_day
	#convert to percentage
	max_cloud_cover = int(maxcloudcover)/100

	#create filters based ons search criteria
	with open(datapath + map) as f:
		geodata = json.load(f)

	ngeodata={}
	for feature in geodata['features']:
		ngeodata['type'] = feature['geometry']['type']
		ngeodata['coordinates'] = feature['geometry']['coordinates']

	# get images that overlap with the AOI
	geometry_filter = {"type": "GeometryFilter","field_name": "geometry", "config": ngeodata}
	start = start +'T00:00:00.000Z'
	end = end + 'T00:00:00.000Z'
	date_range_filter = {"type": "DateRangeFilter", "field_name": "acquired", "config": {"gte": start,"lte": end}}
	cloud_cover_filter = {"type": "RangeFilter", "field_name": "cloud_cover", "config": {"lte": max_cloud_cover}}
	combined_filter = {"type": "AndFilter","config": [geometry_filter, date_range_filter, cloud_cover_filter]}

	# API Key
	f = open(planetauthfile, 'r')
	lines = f.readlines()
	PLANET_API_KEY = lines[0].strip()
	f.close()

	#asset type
	if((int(year) >= 2022) and (int(month) >=5)):
		print('\n8-band SUPERDOVE\n')
		superdove = True
		item_type = "PSScene"
		asset_type = "ortho_analytic_8b_xml"
	else:
		#Dove 4 band
		print('\n4-band dove\n')
		superdove = False
		item_type = "PSScene4Band"
		asset_type = "analytic_xml"


	# API request object including metadata
	search_request = {"item_types": [item_type], "asset_types": [asset_type],"filter": combined_filter}

	# send off the POST request
	search_result = requests.post('https://api.planet.com/data/v1/quick-search',auth=HTTPBasicAuth(PLANET_API_KEY, ''), json=search_request)

	# extract image IDs only
	image_ids = [feature['id'] for feature in search_result.json()['features']]
	thumb_ids = [feature['_links']['thumbnail'] for feature in search_result.json()['features']]
	n_images = len(image_ids)

	if(n_images == 0):
		print('\nNo images found for those search criteria ... Try again')
		print('exiting ...')
		exit()
	else:
		print('found a number of images meeting the search criteria: ', n_images)
		print(image_ids)
		print()
		#  First or last image ID
		id_first = image_ids[0]
		th_first = thumb_ids[0]
		th_url = th_first

		#Get the thumbnail images
		result = 0
		filelist = []
		result = requests.get(th_url, auth=HTTPBasicAuth(PLANET_API_KEY, ''))
		if(result !=0):
			i = 0
			for item in image_ids:
				result = requests.get(thumb_ids[i], auth=HTTPBasicAuth(PLANET_API_KEY, ''))
				thumb_image = planetpreviewpath + str(item) +'.png'
				filelist.append(thumb_image)
				with open(thumb_image, 'wb') as file:
					file.write(result.content)
					print('Got this thumb image: ' ,thumb_image)
				i = i+1

			#copy over to Pcloud, if enabled
			if(t2p == "yes"):
				f = open(authfile, 'r')
				lines = f.readlines()
				username = lines[0].strip()
				password = lines[1].strip()
				f.close()

				conn = PyCloud(username, password, endpoint='nearest')
				conn.uploadfile(files=filelist, path=pcloudpreviewdir)
				print('\n\nUploaded to pCloud: ' , filelist)
				print('\n\n')


		else:
			print('Not able to retrieve previews for your choices...') 
	
#----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
#----------------------------------------------------------------------------------------------
