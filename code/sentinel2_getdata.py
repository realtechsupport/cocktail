# sentinel2_getdata.py
# Get Sentinel2 data products based on an area of interest, cloudcover and date interval
# Preparations:
# 1
# Create an account with Copernicus Open Access Hub (https://scihub.copernicus.eu/dhus)
# You will need a login and pswd to access sentinel2 files
# 2
# Generate a geojson file for area of interest (https://geojson.io/)
# Save the file as somearea.geojson and place a copy on into your data directory (see below)

# ESA quotas:
# https://forum.step.esa.int/t/esa-copernicus-data-access-long-term-archive-and-its-drawbacks/15394/14
# Please note that the maximum number of products that a single user can request on SciHub is 1 every 30 minutes.
# An additional quota limit is applied to users of the APIHub of maximum 20 products every 12 hours.
#
# Usage:
# python3 sentinel2_getdata.py start, end, map, maxcloudcover
# python3 sentinel2_getdata.py date(2021, 7, 24), date(2021, 7, 27), area2.geojson, 20
# ------------------------------------------------------------------------------

import sys, os
import json
import gdal
import otbApplication
import numpy
from zipfile import ZipFile
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date

from helper import *
from sentinel2_helper import *

# Local path and variables
datapath = '/home/blc/cocktail/data/'
inputsfile = datapath + 'settings.txt'

#-------------------------------------------------------------------------------

def main():
	print("\nProceeding with data collection")
	get_sentinel_data()

#--------------------------------------------------------------------------------

def get_sentinel_data():
	try:
        	f = open(inputsfile, 'r')
        	data = f.read()
        	jdata = json.loads(data)
        	f.close()
	except:
        	print('\n...data access error...\n')
	else:
		sentinelrasterpath = jdata['sentinelrasterpath']
		landsat8rasterpath = jdata['landsat8rasterpath']
		vectorpath = jdata['vectorpath']
		collectionpath = jdata['collectionpath']
		rawsatpath = jdata['rawsatpath']
		authfile = jdata['authfile']
		sentinelauthfile = jdata['sentinelauthfile']
		location = jdata['location']
		startdate = jdata['startdate']
		enddate = jdata['enddate']
		maxcloudcover = jdata['maxcloudcover']
		map = jdata['geojsonmap']

	#set sentinel parameters
	maxitems = 1
	platform = 'Sentinel-2'
	product = 'S2MSI1C'
	footprint = geojson_to_wkt(read_geojson(datapath + map))

	starts = startdate.split('_')
	starts_year = int(starts[0])
	starts_month = int(starts[1])
	starts_day = int(starts[2])

	ends = enddate.split('_')
	ends_year = int(ends[0])
	ends_month = int(ends[1])
	ends_day = int(ends[2])

	start = date(starts_year, starts_month, starts_day)
	end = date(ends_year, ends_month, ends_day)

	print('GEOJSON MAP: ', map)
	print('TIMEFRAME: ', startdate, enddate)
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
		products = api.query(footprint, date = (start, end), platformname = platform, producttype = product, cloudcoverpercentage = (0, maxcloudcover))
		products_df = api.to_dataframe(products)
		# ascending=[False] > newest item; ascending=[True] > oldest item;
		products_df_sorted = products_df.sort_values(['ingestiondate'], ascending=[False])
		# usually only 1 (large files, upto 1GB )
		print('\nNumber of items being downloaded: ', maxitems)
		products_df_sorted = products_df_sorted.head(maxitems)
		print('\nGetting this/these item/s: ', products_df_sorted)
		api.download_all(products_df_sorted.index, directory_path = rawsatpath)
		print('\nDownload attempt complete ...  check sentinel folder')
	# catch all exceptions
	except Exception as ex:
		template = "\nAn exception occurred. This is the reported error:\n{1!r}"
		message = template.format(type(ex).__name__, ex.args)
		print (message)
		print('\n... Something went wrong ... see below...')
		print('possible error sources: geojson file, ndays, nmonths and cloud cover setting ...')


	# unpack the package if it has been received
	if(len(products_df_sorted) > 0):
		unpack(rawsatpath)

	tci_path = get_tci_path(rawsatpath)
	jp2_list = [band for band in os.listdir(tci_path) if band [-4:] == '.jp2']

	# two versions here: 1: clip and make thubmnail from the TCI only
	# 2. convert all bands, clip, zip and move to collection

	#convert .jp2 to .tif
	print('\nconverting .jp2 to .tif\n')
	tci_path = tci_path + '/'
	for image in jp2_list:
		timage = image.split('.jp2')[0] + '.tif'
		ds = gdal.Translate(tci_path + timage, tci_path + image)
		ds = None

	tif_list =[band for band in os.listdir(tci_path) if band[-4:] == '.tif']
	print(tif_list) 

	# move and unpack the shapefile to the ROI dir in the vectorpath
	roishapezipfile =  'area2_shape_crop.zip'
	roishape = roishapezipfile.split('.zip')[0] + '.shp'
	roipath = vectorpath + 'roi/'
	roipath_area2crop = roipath + roishapezipfile.split('.zip')[0] + '/'

	# eigentlich only have to unzip the ROI file once..
	shutil.copy(collectionpath + roishapezipfile, roipath)
	with zipfile.ZipFile(roipath + roishapezipfile, 'r') as zip_ref:
		zip_ref.extractall(roipath)

	#clip bands
	warp_options = gdal.WarpOptions(cutlineDSName = roipath_area2crop+roishape, cropToCutline = True)

	for b in tif_list:
		b_new = b.split('.tif')[0] + '_roi' + '.tif'
		print(b, b_new)
		ds = gdal.Warp(tci_path + b_new, tci_path + b, options = warp_options)
		ds = None

	# got this far ----------------------------------------------------------
	# zip up and move to collection, then delete everything in rawsat directory
	# https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory 

#--------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------
