# COCKTAIL
# planet_place_order.py

#Place an order for a PS Superdove asset, based on the image id collected with the planet_get_preview module
#Returns the asset clipped to the specified AOI.
#RTS, Nov 2022

#--------------------------------------------------------------------------------------------
# You need a valid planet lab API key to use this routine
# Place the key in the auth folder (or modify the access method)
# planet API V2

# Usage: -------------------------------------------------------------------------------------
# > python3 planet_place_order.py
#
# Enter choice at the prompt:
# image id, copied from the preview (on pCloud or on the VM), AOI 
# assets, if found, may not be ready immediately. Script tries several times before timing out.
# CTRL C to stop and then try again later...

#-------------------------------------------------------------------------------
import sys, os
import json, requests
from requests.auth import HTTPBasicAuth
from planet_helper import *
from pcloud import PyCloud

# Local path and variables
datapath = '/home/ghemanth2578/cocktail/data/'
inputsfile = datapath + 'settings.txt'

#----------------------------------------------------------------------------------------------
def main():

	elements = []
	print('\nUse this routine to get a planet lab satellite asset, clipped to an AOI.')
	print('\nEnter the image ID and the name of the AOI.')
	print('Example: 20220806_021247_74_248b area2_square.geojson')
	response = input("\nEnter your choices: ")
	try:
		elements = response.split(' ')
		id  = elements[0]
		map = elements[1]
	except:
		id = 'na'
		map = 'na'
		print('\nInput is empty - exiting')
		exit()

	get_planet_data_v2(id, map)

#----------------------------------------------------------------------------------------------
def get_planet_data_v2(id, map):

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
		rawsatpath = jdata['rawsatpath']
		authfile = jdata['authfile']
		planetauthfile = jdata['planetauthfile']
		location = jdata['location']
		pcloudplanet = jdata['pcloudplanet']
		t2p = jdata['T2P']

	print('\nYour inputs: ' , id, map)
	print()
	# --------------------------------------------------------------------------

	# API Key
	f = open(planetauthfile, 'r')
	lines = f.readlines()
	PLANET_API_KEY = lines[0].strip()
	f.close()

	#AOI
	try:
		with open(datapath + map) as f:
  			geodata = json.load(f)
	except:
		print('Could not find the AOI file...retry...')
		exit()

	if(map  != 'na'):
		ngeodata={}
		for feature in geodata['features']:
  			ngeodata['type'] = feature['geometry']['type']
  			ngeodata['coordinates'] = feature['geometry']['coordinates']


	# Superdove? Use the input id to assess
	id_date = id.split('_')[0]
	id_year = id_date[0:4]
	id_month = id_date[4:6]
	constellation = 'na'
	if((int(id_year) >= 2022) and (int(id_month) >= 4)):
		constellation = 'superdove'
		print('Requesting SUPERdove asset.')
	else:
		print('Requesting dove asset.')

	if(constellation == 'superdove'):
		single_product_8b = [{"item_ids" : [id], "item_type" : "PSScene","product_bundle" : "analytic_8b_sr_udm2"}]
		single_product = single_product_8b
		end_tag = '8b_clip.tif'
		dir_tag = '/PSScene/'
	else:
		single_product_4b = [{"item_ids" : [id], "item_type" : "PSScene4Band","product_bundle" : "analytic"}]
		single_product = single_product_4b
		end_tag = '_clip.tif'
		dir_tag = '/PSScene4Band/'

	# Order V2 - with clipping
	orders_url = 'https://api.planet.com/compute/ops/orders/v2'

	# Requests to work with api
	auth = HTTPBasicAuth(PLANET_API_KEY, '')
	headers = {'content-type': 'application/json'}

        # Clip tool
	clip = {"clip": {"aoi": ngeodata}}

        # Create an order request with the clipping tool
	request_clip = {"name": "just clip", "products": single_product, "tools": [clip]}

	# Download to the VM and poll process
	clip_order_url = place_order(request_clip, auth, orders_url, headers)
	num_loops = 100
	poll_for_success(clip_order_url, auth, num_loops)
	savepath = planetrasterpath
	downloaded_clip_files = download_order(savepath, clip_order_url, auth)
	print('\nDownloaded the asset.')

	#Find the clipped file in the downloaded package
	sdir = planetrasterpath
	newest_dir = max([os.path.join(sdir,d) for d in os.listdir(sdir)], key=os.path.getmtime)
	ssdir = newest_dir + dir_tag
	dirlist = os.listdir(ssdir)

	target_file = 'na'
	for item in dirlist:
		if(end_tag in item):
			target_file = item

	#Rename the file based on the actual download
	date_parts = target_file.split('_')[0]
	year = date_parts[0:4]
	month = date_parts[4:6]
	day = date_parts[6:8]
	date = month + day + '_' + year
	place = map.split('.')[0]
	
	# Copy to the collection directory
	try:
		shutil.copy(ssdir + target_file, collectionpath +  target_file)
		print('Copied asset to the collection')

		if(constellation == 'superdove'):
			newname = place + '_' + date + '_' + '8bands.tif'
		else:
			newname = place + '_' + date + '_' + '4bands.tif'
	
		os.rename(collectionpath + target_file, collectionpath + newname)

	except:
		print('\nSomething went wrong..Could not copy the asset into the collection..')
		exit()

	# Copy over to PCloud, if enabled
	if(t2p == "yes"):
		f = open(authfile, 'r')
		lines = f.readlines()
		username = lines[0].strip()
		password = lines[1].strip()
		f.close()

		filelist = [collectionpath + newname]

		print('\nCopying to pCloud: ', filelist)
		conn = PyCloud(username, password, endpoint='nearest')
		conn.uploadfile(files=filelist, path=pcloudplanet)
		print('\nFile transfer complete\n')

#----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
#----------------------------------------------------------------------------------------------
