# sentinel2_getdata.py bandselection
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
# path_filter
# https://github.com/sentinelsat/sentinelsat/issues/540#issuecomment-920883495

# Usage:
# python3 sentinel2_getdata.py [tci or all)
# python3 sentinel2_getdata.py (bandselection)
# ------------------------------------------------------------------------------

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
datapath = '/home/blc/cocktail/data/'
inputsfile = datapath + 'settings.txt'

#-------------------------------------------------------------------------------

def main():
	for arg in sys.argv[1:]:
		print("Received this input: ", arg)

	bandselection = arg.strip()

	if((bandselection == 'tci') or (bandselection == 'all')):
		print("Getting sentinel2 data with this band selection: ", bandselection)
		get_sentinel2_data(bandselection)
	else:
		print("input arguments accepted are:  tci or all ONLY. Try again.")
		exit()

#--------------------------------------------------------------------------------

def get_sentinel2_data(bandselection):
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
		pclouddir = jdata['pdir']

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

		# ISSUE using the filter option...code has workaround...
		'''
		# https://github.com/sentinelsat/sentinelsat/issues/540
		if(bandselection == 'tci'):
			pathfilter = make_path_filter("*_tci.jp2")
			api.download_all(products_df_sorted.index, directory_path = rawsatpath, nodefilter = pathfilter)
		else:
			api.download_all(products_df_sorted.index, directory_path = rawsatpath)
		'''
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

	# get only the bands requested
	if(bandselection == 'tci'):
		jp2_list = [band for band in os.listdir(tci_path) if band [-7:] == 'TCI.jp2']
	else:
		jp2_list = [band for band in os.listdir(tci_path) if band [-4:] == '.jp2']

	#convert .jp2 to .tif
	print('\nconverting .jp2 to .tif\n')
	tci_path = tci_path + '/'
	for image in jp2_list:
		timage = image.split('.jp2')[0] + '.tif'
		ds = gdal.Translate(tci_path + timage, tci_path + image)
		ds = None

	tif_list =[band for band in os.listdir(tci_path) if band[-4:] == '.tif']
	#print(tif_list)

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
		if('TCI' in b):
			tci_tif = b
		ds = gdal.Warp(tci_path + b_new, tci_path + b, options = warp_options)
		ds = None

	# send tci thumbnail to pcloud
	if(bandselection == 'tci'):
		#convert to jpeg and reduce in size
		tci_jpeg = tci_tif.split('.tif')[0] + '.jpeg'
		ds = gdal.Translate(tci_path + tci_jpeg, tci_path + tci_tif, format='JPEG', width = 800, height=0, scaleParams=[[]])
		ds = None
		#sent to pcloud
		print('\nSending to pCloud..')
		filelist = [tci_path +  tci_jpeg]
		send_to_pcloud(filelist, authfile, pclouddir)
	else:
		print('zip up and move to collection for processing...')
		# toDO zip up and move to collection ...
		# https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory

	#toDO delete content of rawsat ...

#--------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#---------------------------------------------------------------------------------
