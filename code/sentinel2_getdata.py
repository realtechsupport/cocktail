# COCKTAIL
# sentinel2_getdata.py
# RTS, July, October 2022
# Update May 2023 - option to get only 10m resolution bands
# Output file saved to collections folder
#--------------------------------------------------------------------------------------------

# The script collects all the sentinel bands of the specified time and cloud conditions
# It selects the area based on the geojson file specified in the settings file
# and clips the files to the ROI specified in the zipped shapefile specified in the settings file
# Files are saved without the term 'clip'"
# T50LKR_20170717T023939_B01.tif
# T50LKR_20170717T023939_B02.tif
# etc
# It zipps up the result and saves it - based on the name of the geojson file
# and the satellite collection date -  to the collection folder.
# for example: area2_square_0801_2022.zip
#
# Prepare satellite assets with this routine and apply to otb_difference_ndbi.py to
# find difference in built up areas across two dates
#--------------------------------------------------------------------------------------------
# sentinelsat version 1.1.1
# https://sentinelsat.readthedocs.io/en/v1.1.1/api_reference.html

# Preparations:
# 1
# Create an account with Copernicus Open Access Hub (https://scihub.copernicus.eu/dhus)
# You will need a login and pswd to access sentinel2 files
# Put the Coperniculs credentials in a .txt file in the auth folder
# line 1: user
# line 2: pswd

# 2
# Generate a geojson file for area of interest (https://geojson.io/)
# Save the file as somearea.geojson and place a copy on into your data directory (see below)

#3
# Create from that geojson file shapefiles to crop the resultant imagebands and compress (zip)

#4
# Update the settings.txt file with your variables (area.geojson, roi.zip, dates)

# -------------------------------------------------------------------------------------------
# ESA quotas:
# https://forum.step.esa.int/t/esa-copernicus-data-access-long-term-archive-and-its-drawbacks/15394/14
# "Please note that the maximum number of products that a single user can request on SciHub is 1 every 30 minutes.
# An additional quota limit is applied to users of the APIHub of maximum 20 products every 12 hours".
#
# path_filter - not working. See below for workaround
# https://github.com/sentinelsat/sentinelsat/issues/540#issuecomment-920883495

# Usage: -------------------------------------------------------------------------------------
# activate OTB, run script, follow prompts
# > conda activate OTB
# > python3 sentinel2_getdata.py
#
# enter choices at the prompt
# inputs: bandselection, now, uuid
# if the second input is empty, end date in settings.txt will be used
# do   1. tci now ... to see if there is a useable image
# then 2. all now ... to fetch the bands and save them in the collection
# or
#	  tci ... to get the latest tci between dates in the settings.txt
#         all ... to get the bands between dates in the settings.txt
#	  71d7edef-292c-4f4e-af40-72c3f0e9eb64 .. a uuid to get a known asset
#
# if the script does not fetch an asset within 30 seconds, something might be amiss with the connection
# CTRL C to stop and then try again later...
#
# Start and End dates should not be too far appart (not sure on upper bound, but typically a month or so).
#
# Note on downloading -------------------------------------------------------------------------
# download speeds from ESA vary ... can be slow 200kB/s even ...
# increase download speeds my placing the Cocktail server in Europe
# https://github.com/sentinelsat/sentinelsat/issues/187
# ...move closer to the DHuS endpoint ...using a national mirror or for instance using a server located close to ESA in Frankfurt.
#---------------------------------------------------------------------------------------------

import sys, os
import json
import gdal
import otbApplication
import numpy
from zipfile import ZipFile
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt, make_path_filter
from datetime import date

from helper import *
from sentinel2_helper import *

# Local path and variables
datapath = '/home/marcbohlen/cocktail/data/'
inputsfile = datapath + 'settings.txt'

#----------------------------------------------------------------------------------------------
def main():

	inputs = []
	bandseletion = 'na'
	enddate = 'na'
	uuid = 'na'

	print('You can use this routine to get the TCI or all bands of a Sentinel2 asset from any region specified in a geojson file.')
	print('Edit the start and end dates in the settings.txt file.')
	print('\nTo get the latest TCI between those preset dates, enter: tci')
	print('To get the latest set of all bands between those dates, enter: all')
	print('To get only the 10m resolution bands between those dates, enter: 10m')
	print('To get the latest TCI from the present, enter: tci now')
	print('To get the lastest set of all bands from the present, enter: all now')
	print('To get the lates set of 10m resolution bands from the preent, enter: 10m now')
	print('To get all bands from a known UUID, enter that long UUID: a-b-c-d-e')


	response = input("\nEnter your choice: ")
	long = 20
	try:
		elements = response.split(' ')
		bandselection = elements[0]
		enddate = elements[1]
	except:
		if(len(response) > long):
			uuid = response
			bandselection = 'all'
		else:
			bandselection = response

	if((bandselection == 'tci') or (bandselection == 'all') or (bandselection == '10m')):
		print('\nGetting the sentinel2 asset with choices: ', bandselection, enddate, uuid)
		get_sentinel2_data(bandselection, enddate, uuid)
	else:
		print("\ntci, all or the uiid is required. Try again...\n")

#----------------------------------------------------------------------------------------------
def get_sentinel2_data(bandselection, enddate, uuid):

	try:
        	f = open(inputsfile, 'r')
        	data = f.read()
        	jdata = json.loads(data)
        	f.close()
	except:
        	print('\n...data access error...check settings.txt\n')

	else:
		sentinelrasterpath = jdata['sentinelrasterpath']
		landsat8rasterpath = jdata['landsat8rasterpath']
		vectorpath = jdata['vectorpath']
		collectionpath = jdata['collectionpath']
		rawsatpath = jdata['rawsatpath']
		authfile = jdata['authfile']
		sentinelauthfile = jdata['sentinelauthfile']
		location = jdata['location']
		sent_startdate = jdata['sent_startdate']
		sent_enddate = jdata['sent_enddate']
		maxcloudcover = jdata['maxcloudcover']
		goodpixelthreshold = jdata['goodpixelthreshold']
		map = jdata['geojsonmap']
		pclouddir = jdata['pdir']
		sentinelpclouddir = jdata['pdir_sentinel']
		logfile = jdata['logfile']
		roi = jdata['roi']
		roipath = jdata['roipath']

	#set sentinel parameters
	maxitems = 1
	platform = 'Sentinel-2'
	product = 'S2MSI1C'
	footprint = geojson_to_wkt(read_geojson(datapath + map))

	starts = sent_startdate.split('_')
	starts_year = int(starts[0])
	starts_month = int(starts[1])
	starts_day = int(starts[2])
	start = date(starts_year, starts_month, starts_day)

	if(enddate == 'na'):
		ends = sent_enddate.split('_')
		ends_year = int(ends[0])
		ends_month = int(ends[1])
		ends_day = int(ends[2])
		end = date(ends_year, ends_month, ends_day)
	else:
		end = 'NOW'
		print('Checking latest available sentinel asset in the selected geojson region with below-threshold cloud cover.')

	print('GEOJSON MAP: ', map)
	print('MAX CLOUD COVER: ', maxcloudcover)
	print('PLATFORM, PRODUCT: ', platform, product)
	print('START, END: ', start, end)

	#get the ESA login info
	f = open(sentinelauthfile, 'r')
	lines = f.readlines()
	username = lines[0].strip()
	password = lines[1].strip()
	f.close()

	api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')
	
	#fetch the data
	try:
		this_uuid = 'na'

		if(uuid == 'na'):
			products = api.query(footprint, date = (start, end), platformname = platform, producttype = product, cloudcoverpercentage = (0, maxcloudcover))
			products_df = api.to_dataframe(products)
			# ascending=[False] > newest item; ascending=[True] > oldest item;
			products_df_sorted = products_df.sort_values(['ingestiondate'], ascending=[False])
			products_df_sorted = products_df_sorted.head(maxitems)
			this_uuid = products_df_sorted['uuid'][0]
			print('\nCorresponding uuid: ', this_uuid)

		else:
			print('\Manually entered uuid: ', uuid)
			this_uuid = uuid

		api.download(this_uuid, directory_path = rawsatpath)

		# https://github.com/sentinelsat/sentinelsat/issues/540
		#if(bandselection == 'tci'):
		#	pathfilter = make_path_filter("*_tci.jp2")
		#	api.download_all(products_df_sorted.index, directory_path = rawsatpath, nodefilter = pathfilter)
		#else:
		#	api.download_all(products_df_sorted.index, directory_path = rawsatpath)

		print('\nDownload attempt complete ...  check sentinels folder within rasterimages')

	# catch all exceptions
	except Exception as ex:
		template = "\nAn exception occurred. This is the reported error:\n{1!r}"
		message = template.format(type(ex).__name__, ex.args)
		print (message)
		print('\n... Something went wrong ... see below...')
		print('Possible error sources: gateway timeout, geojson file, start and end dates, cloud cover setting.')
		exit()

	# unpack the package if it has been received
	if(this_uuid != 'na'):
		unpack(rawsatpath)

	tci_path = get_tci_path(rawsatpath)
	print(tci_path)

	# get only the bands requested
	if(bandselection == 'tci'):
		jp2_list = [band for band in os.listdir(tci_path) if band [-7:] == 'TCI.jp2']
	
	elif(bandselection == '10m'):
		jp2_list =  [band for band in os.listdir(tci_path) if ((band [-7:] == 'B02.jp2') or (band [-7:] == 'B03.jp2') or (band [-7:] == 'B04.jp2') or (band [-7:] == 'B08.jp2'))]
	else:
		jp2_list = [band for band in os.listdir(tci_path) if band [-4:] == '.jp2']


	print(jp2_list)

	#convert .jp2 to .tif
	print('\nConverting .jp2 to .tif\n')
	tci_path = tci_path + '/'
	for image in jp2_list:
		timage = image.split('.jp2')[0] + '.tif'
		ds = gdal.Translate(tci_path + timage, tci_path + image)
		ds = None

	tif_list =[band for band in os.listdir(tci_path) if band[-4:] == '.tif']

	# move and unpack the shapefile to the ROI dir in the vectorpath
	roishape = roi.split('.zip')[0] + '.shp'

	# eigentlich only have to unzip the ROI file once..
	shutil.copy(collectionpath + roi, roipath)
	with zipfile.ZipFile(roipath + roi, 'r') as zip_ref:
		zip_ref.extractall(roipath)

	#clip bands
	print('\nPerforming the clipping operation to the ROI')
	warp_options = gdal.WarpOptions(cutlineDSName = roipath + roishape, cropToCutline = True)
	for b in tif_list:
		#b_new = b.split('.tif')[0] + '_roi' + '.tif'
		b_new = b
		print(b, b_new)
		if('TCI' in b):
			tci_tif = b_new
		ds = gdal.Warp(tci_path + b_new, tci_path + b, options = warp_options)
		ds = None

	# Check image stats (75% valid min, resize and send tci thumbnail to pcloud
	if(bandselection == 'tci'):
		#convert to jpeg and reduce in size
		tci_jpeg = tci_tif.split('.tif')[0] + '.jpeg'
		ds = gdal.Translate(tci_path + tci_jpeg, tci_path + tci_tif, format='JPEG', width = 800, height=0, scaleParams=[[]])
		ds = None

		#check stats
		minimum = 0
		#threshold = 50
		percentage_good_pixels = check_image(tci_path + tci_jpeg, minimum)

		if(percentage_good_pixels > int(goodpixelthreshold)):
			#send to pcloud
			print('\nImage passes test. Percentage of non-black pixels:', percentage_good_pixels)
			print('Sending to pCloud..')
			filelist = [tci_path +  tci_jpeg]
			send_to_pcloud(filelist, authfile, sentinelpclouddir)

		else:
			print('\nImage does not pass test. Percentage of non-black pixels: ', percentage_good_pixels)
			print('NOT sending to pCloud..')

		#create log message
		timestamp = create_timestamp(location)
		comment = timestamp + ': TCI test: ' + str(percentage_good_pixels) + ' for uuid ' + this_uuid

	else:
		print('Zip up and move to collection for processing...')
		roi_list =[band for band in os.listdir(tci_path) if band[-4:] == '.tif']

		maparea = map.split('.geojson')[0]
		monthday = roi_list[0].split('_')[1][4:8]
		year = roi_list[0].split('_')[1][0:4]
		sentinelasset = maparea + '_' + monthday + '_' + year + '_sentinel2'

		#print(sentinelasset)

		if(os.path.exists(tci_path +'/temp')):
			pass
		else:
			os.mkdir(tci_path + '/temp')

		for roi in roi_list:
			shutil.copy(tci_path + roi, tci_path + '/temp/' + roi)

		archivename = os.path.join(collectionpath, sentinelasset)
		datasource = os.path.join(tci_path, 'temp')
		shutil.make_archive(archivename, 'zip', datasource)

		#create log message
		timestamp = create_timestamp(location)
		comment = timestamp + ': All bands in collection for uuid ' + this_uuid

	#log the results
	print('\nAdding log entry...')
	method = 'a'
	log(datapath + logfile, comment, method)

	# show saved loction
	print('\nFinal .tif file saved to collections folder.')

	# delete content of rawsat
	print('\nDeleting temporary files to save storage space...')
	shutil.rmtree(rawsatpath)
	os.makedirs(rawsatpath)

#----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
#----------------------------------------------------------------------------------------------
