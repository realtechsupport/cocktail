# -*- coding: utf-8 -*-
# Sentinel2_helper.py
# utilities to assist with processing Sentinel2 imagery
# RTS, spring 2021
#-------------------------------------------------------------------------------
import sys, os, shutil
import zipfile
from pathlib import Path
#import rasterio
#import rioxarray
#from rasterio import Affine
#from rasterio.enums import Resampling
import gdal
# ------------------------------------------------------------------------------

def unpack(searchpath):
	for r, d, f in os.walk(searchpath):
		for file in f:
			if file.endswith(".zip"):
				zfile = file
				print('uncompressing this file: ', zfile)
				break

	#unzip compressed_file_name.zip
	with zipfile.ZipFile(searchpath + zfile,"r") as zip_ref:
		zip_ref.extractall(searchpath)

	print('Finished extracting data from zip files')

#-------------------------------------------------------------------------------

def get_imageroot(searchpath):
#find the full path of the true color image (TCI) and the path to all image bands
	TCI = 'na'
	key = "TCI.jp2"
	for spath in Path(searchpath).rglob('*.SAFE'):
	  result = spath.name

	SAFEpath = searchpath + result + '/GRANULE/'
	for root, dir, files in os.walk(SAFEpath):
		for file in files:
			if file.endswith(key):
				TCI = (os.path.join(root, file))

	imageroot = TCI.split(key)[0]
	return(imageroot)

#-------------------------------------------------------------------------------

def get_tci_path(searchpath):
#find the full path of the true color image (TCI) and the path to all image bands
	TCI = 'na'
	key = "TCI.jp2"
	for spath in Path(searchpath).rglob('*.SAFE'):
	  result = spath.name

	SAFEpath = searchpath + result + '/GRANULE/'
	for root, dir, files in os.walk(SAFEpath):
		for file in files:
			if file.endswith(key):
				TCI = (os.path.join(root, file))

	tci_path = os.path.dirname(TCI)
	return(tci_path)
#-------------------------------------------------------------------------------

def get_tci(searchpath):
#find the full path of the true color image (TCI) and the path to all image bands
	TCI = 'na'
	key = "TCI.jp2"
	for spath in Path(searchpath).rglob('*.SAFE'):
	  result = spath.name

	SAFEpath = searchpath + result + '/GRANULE/'
	for root, dir, files in os.walk(SAFEpath):
		for file in files:
			if file.endswith(key):
				TCI = (os.path.join(root, file))
	return(TCI)
#-------------------------------------------------------------------------------
'''
def convert_tci_tif(tci, searchpath, img_type):
	ds = gdal.Open(tci)
	dst_filename = searchpath + img_type
	ds = gdal.Translate(dst_filename, ds)
	tif_img = rasterio.open(dst_filename)
	ds = None
'''
#-------------------------------------------------------------------------------

def fdi(nir, rededge, swir, lambda_nir, lambda_red, lambda_swir):
	# fdi = NIR - X
	# X =  REDedge2 + (SWIR1 - REDedge2) * L
	# L = 10*((lambda_nir - lambda_red) / (lambda_swir - lambda_red))

	# NIR: band8, 10m res
	# REDedge2: band6, 20m res -> convert to 10m
	# SWIR1: band11,   20m res -> convert to 10m

	L = 10 * (((lambda_nir - lambda_red) / (lambda_swir - lambda_red)))
	#print('this is the value of L: ', L)
	X = rededge.astype(float) + ((swir.astype(float) - rededge.astype(float)) * L)
	fdi = nir.astype(float) - X
	return(fdi)
#----------------------------------------------------------------------------------

def ndbi(b08, b11):
	#reference: V - A New Three Band Index for Identifying Urban Areas using Satellite Images
	#dnbi = (MIR - TIR) / (MIR + TIR)
	dbni = ((b08.astype(float) - b11.astype(float))) / (b08 + b11)
	return (ndbi)

#-------------------------------------------------------------------------------

def ndwi(green, nir):
	#https://github.com/sentinel-hub/custom-scripts/tree/master/sentinel-2/ndwi
	#ndwi = (green - nir) / (green + nirir)
	ndwi = (green.astype(float) - nir.astype(float)) / (green + nir)
	return(ndwi)
#-------------------------------------------------------------------------------

def ndvi(red, nir):
	#ndvi = (nir-red) / (nir+read)
	ndvi = (nir.astype(float) - red.astype(float)) / (nir + red)
	return(ndvi)
#-------------------------------------------------------------------------------

def nbr(nir, swir):
	#https://www.l3harrisgeospatial.com/docs/backgroundburnindices.html
	#ndwi = (nir - swir) / (nir + swir)
	nbr = (nir.astype(float) - swir.astype(float)) / (nir + swir)
	return(nbr)
#-------------------------------------------------------------------------------

def bsi(red, blue, nir, swir):
	#BSI = ((Red+SWIR) - (NIR+Blue)) / ((Red+SWIR) + (NIR+Blue))
	num = (red.astype(float) + swir.astype(float)) - (nir.astype(float) + blue.astype(float))
	denom = (red.astype(float) + swir.astype(float)) + (nir.astype(float) + blue.astype(float))
	bsi = num / denom
	return(bsi)
#-------------------------------------------------------------------------------

def create_name(prefix, imageroot, geojsonpath, map):
	#create the name with date and location
	parts = imageroot.split('_')
	lastpart = parts[-2]                                  #second last element
	date = lastpart[0:8]
	geolocation = (geojsonpath + map).split('/')[-1]
	location = geolocation.split('.')[0]
	newfilename = prefix + '_' + location + '_' + date
	return(newfilename)
#-------------------------------------------------------------------------------
'''
def convert_jp2_tif(searchpath, img_type, refband, result_img):
	#result_img in the searchpath
	img_type_path = searchpath + img_type
	img_type_tif = rasterio.open(img_type_path, 'w', driver='Gtiff',
                          width=refband.width, height=refband.height,
                          count=1,
                          crs=refband.crs,
                          transform=refband.transform,
                          dtype='float64' 					#'uint16'
                          )
	img_type_tif.write(result_img)
# ------------------------------------------------------------------------------

def convert_ccr(searchpath, img_type, target_epsg, img_ccr_type):
	img_type_path = searchpath + img_type
	img_type_tif = rasterio.open(img_type_path)
	rds = rioxarray.open_rasterio(img_type_tif)
	rds_4326 = rds.rio.reproject(target_epsg)
	rds_4326.rio.to_raster(searchpath + img_ccr_type)
#-------------------------------------------------------------------------------

def resample(datapath, imageroot, bandname, scale_factor):
	inputfile = imageroot + bandname

	with rasterio.open(inputfile) as dataset:
		t = dataset.transform
		# rescale the metadata
		transform = Affine(t.a / scale_factor, t.b, t.c, t.d, t.e / scale_factor, t.f)
		height = dataset.height * scale_factor
		width = dataset.width * scale_factor

		kwds = dataset.profile
		kwds.update(transform=transform, driver='JP2OpenJPEG', height=height, width=width)  #driver='GTiff'

		# resample data to target shape
		data = dataset.read(out_shape=(dataset.count, height, width), resampling=Resampling.bilinear)
		outputfile = 'rescaled_' + bandname
		with rasterio.open(datapath + outputfile, 'w', **kwds) as dst:
			dst.write(data)

	return(outputfile)
#-------------------------------------------------------------------------------
'''
def archive(searchpath, archivepath, REUSE, ARCHIVE):
	destination = ''
	zip = ''

	if(REUSE == True):
		try:
			for root, dir, files in os.walk(searchpath):
				for file in files:
					if file.endswith(".zip"):
						print('\nfound: ', file)
						zip = (os.path.join(root, file))
						destination = archivepath + file
						shutil.move(zip, destination)
						print('moving zip to archive for now')
						break
		except:
			print('\ncould not move sentinel zip files to archive...')

	#otherwise just delete everything in the sentinel folder
	try:
		shutil.rmtree(searchpath)
		print('emptying the search directory')
	except:
		pass

	print('recreating directory: ', searchpath)
	os.makedirs(searchpath)

	#restore according to your wishes
	if((ARCHIVE == True) and (REUSE == True)):
		try:
			shutil.copy(destination, zip)
			print('sentinel zipfile in archive and sentinel folder')
		except:
			print('no sentinel data found, cant copy back')

	if((ARCHIVE == False) and (REUSE == True)):
		try:
			shutil.move(destination, zip)
			print('sentinel zipfile in sentinel folder')
		except:
			print('no sentinel data found, cant move')

	if((ARCHIVE == False) and (REUSE == False)):
		pass

	if((ARCHIVE == False) and (REUSE == True)):
		try:
			os.remove(destination)
		except:
			print('saving nothing')
# ------------------------------------------------------------------------------
