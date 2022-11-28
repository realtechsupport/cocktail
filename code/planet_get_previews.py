# COCKTAIL
# planet_get_previews.py
# Get thumbmnail size perviews of a scene based on AOI, start date, number of days and cloudcover
# RTS, Nov 2022
#--------------------------------------------------------------------------------------------
# You need a valid planet lab API key to use this routine
# Place the key in the auth folder (or modify the code to your liking)
# planet API V1

# Usage: -------------------------------------------------------------------------------------
# > python3 planet_get_previews.py
#
# Enter choices at the prompt
# inputs: geojson, target date, number of days, max cloudcover
# Start date and number days translate to search date range (1 to max 30 days, must be within the same month)
# Make sure the selected geojson map is saved to the data folder

# Updated for SuperDove
# https://tinyurl.com/superdoved
# https://tinyurl.com/superdove8bands
# https://tinyurl.com/355cz2kc

# Asset requests after May 2022 will fetch SuperDove 8-band data.
# Asset requests before that data get Dove 4-band data.
# If enabled, thumb images will be copied ove to pCloud
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
	print('\nEnter four pieces of information: ')
	print('The name of the geojson file, target date, number of days from target and max cloud cover.')
	print('Enter the date in year-month-day (2021-05-12) format number days and cloud cover as integers.')
	print('Example: area2_square.geojson 2022-08-01 5 25 {space separated}')
	print('if you do not enter any choices, default values from the settings.txt file will be used.')

	response = input("\nEnter your choices: ")
	try:
		elements = response.split(' ')
		map_geojson = elements[0]
		ptargetdate = elements[1]
		ndays = elements[2]
		maxcloud = elements[3]
	except:
		map_geojson = 'na'
		ptargetdate = 'na'
		maxcloud = 'na'
		ndays = 1
		print('\nInput is incomplete ... try again')


	get_planet_data_v1(map_geojson, ptargetdate, ndays, maxcloud)

#----------------------------------------------------------------------------------------------
def get_planet_data_v1(map_geojson, ptargetdate, ndays, maxcloud):

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

	# --------------------------------------------------------------------------

	# Convert cloudcover to percentage
	max_cloud_cover = int(maxcloudcover)/100

	# Create filters based ons search criteria
	with open(datapath + map) as ffile:
		geodata = json.load(ffile)

	ngeodata={}
	for feature in geodata['features']:
		ngeodata['type'] = feature['geometry']['type']
		ngeodata['coordinates'] = feature['geometry']['coordinates']

	# API Key
	f = open(planetauthfile, 'r')
	lines = f.readlines()
	PLANET_API_KEY = lines[0].strip()
	f.close()

	# Create the search dates
	start = targetdate
	# Prevent date format snafu ..
	try:
		info = targetdate.split('-')
	except:
		info = targetdate.split('_')

	dates_range_filter = []
	day = info[2]
	intday = int(day)

	begin = int(day)
	finish = begin + int(ndays)
	# Limits on end of month
	if(finish >= 30):
		finish = 30

	# Create start and end dates
	for i in range(begin, finish):
		month = info[1]
		year = info[0]
		start_day = intday
		end_day = str(intday + 1).zfill(2)
		startdate = info[0] + '-' + info[1] + '-' + str(start_day).zfill(2) + 'T00:00:00.000Z'
		enddate = info[0] + '-' + info[1] + '-' + end_day + 'T00:00:00.000Z'
		intday = intday + 1

		#starts.append(startdate)
		#ends.append(enddate)
		drf = {"type": "DateRangeFilter", "field_name": "acquired", "config": {"gte": startdate,"lte": enddate}}
		dates_range_filter.append(drf)

	# Asset type
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
		'''
		#update after 1/2023
		# https://developers.planet.com/docs/apis/data/psscene3-4band-deprecation/
		item_type = "PSScene"
		asset_type = "ortho_analytic_4b_xml"
		'''

	# Set geometry and cloud filters
	geometry_filter = {"type": "GeometryFilter","field_name": "geometry", "config": ngeodata}
	cloud_cover_filter = {"type": "RangeFilter", "field_name": "cloud_cover", "config": {"lte": max_cloud_cover}}

	# Get Pcloud creds
	if(t2p == "yes"):
		f = open(authfile, 'r')
		lines = f.readlines()
		username = lines[0].strip()
		password = lines[1].strip()
		f.close()

	# Define the AOI with shapely
	aoi = geometry.shape(ngeodata)

	# Launch the search for each date set
	for date_set in dates_range_filter:
		combined_filter = {"type": "AndFilter","config": [geometry_filter, date_set, cloud_cover_filter]}
		# API request object including metadata
		search_request = {"item_types": [item_type], "asset_types": [asset_type],"filter": combined_filter}

		# send off the POST request
		search_result = requests.post('https://api.planet.com/data/v1/quick-search',auth=HTTPBasicAuth(PLANET_API_KEY, ''), json=search_request)

		# extract image IDs only
		image_ids = [feature['id'] for feature in search_result.json()['features']]
		thumb_ids = [feature['_links']['thumbnail'] for feature in search_result.json()['features']]
		geo_infos = [feature['geometry'] for feature in search_result.json()['features']]
		n_images = len(image_ids)

		if(n_images == 0):
			print('\nNo matching results found for that date\n')
			print('Trying next date ...')
		else:
			print('Found a number of candidates meeting the search criteria: ', n_images)
			print(image_ids)
			print()
			#  First ID
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
					res = requests.get(thumb_ids[i], auth=HTTPBasicAuth(PLANET_API_KEY, ''))
					g = geometry.shape(geo_infos[i])
					#Check if aoi is inside candidate geometry
					if(g.contains(aoi)):
						print('\nCandidate contains the AOI')
						thumb_image = planetpreviewpath + str(item) +'.png'
						filelist.append(thumb_image)
						with open(thumb_image, 'wb') as file:
							file.write(res.content)
							print('Got the corresponding thumb image: ' , thumb_image)

						if(t2p == "yes"):
							conn = PyCloud(username, password, endpoint='nearest')
							conn.uploadfile(files=filelist, path=pcloudpreviewdir)
							print('Uploaded to pCloud: ' , filelist)
							print('\n')


					else:
						print('Candidate does not fully cover the aoi..')

					i = i+1

			else:
				print('Not able to retrieve previews for that choice ...')

#----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
#----------------------------------------------------------------------------------------------
