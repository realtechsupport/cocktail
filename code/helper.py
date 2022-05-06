# -*- coding: utf-8 -*-
# helper.py
# routines to support the OTB-QGIS toolchain COCKTAIL
# RTS, Jan/April 2022
# ------------------------------------------------------------------------------
import os, sys, numpy
from datetime import datetime
import gdal
from PIL import Image

import pytz
import glob, shutil, zipfile
from zipfile import ZipFile
from pcloud import PyCloud
#------------------------------------------------------------------------------
# Create a time stamp, based on location
def create_timestamp(location):
    tz = pytz.timezone(location)
    now = datetime.now(tz)
    current_time = now.strftime("%d-%m-%Y-%H-%M")
    return(current_time)

#-------------------------------------------------------------------------------
# Make all posssible combinations of two different parameter vector inputs
def change_settings(path, infile, token1_name, token1_value, token2_name, token2_value, change1, change2, outfile):
    file = open(path + infile, 'r')
    inlines = file.readlines()
    i=0; j=0

    for line in inlines:
        i = i + 1
        j = j + 1
        if((token1_name in line) and (token1_value in line)):
            t1 = i
        elif((token2_name in line) and (token2_value in line)):
            t2 = j

    inlines[t1-1] =  '\t' + '"' + token1_name + '" ' + ":" + ' "' + change1 + '"' + ',\n'
    inlines[t2-1] =  '\t' + '"' + token2_name + '" ' + ":" + ' "' + change2 + '"' + ',\n'

    file = open(path + outfile, 'w')
    file.writelines(inlines)
    file.close()

#-----------------------------------------------------------------------------
# Precision, Recall and Fscore gleaned from a multi-class confusion matrix
# https://en.wikipedia.org/wiki/Precision_and_recall
def get_classifier_statistics(location, datapath, confusion_matrix, save):
	stats = []
	# Load the data
	d = numpy.genfromtxt(datapath + confusion_matrix, delimiter=',', dtype = int)
	# Calculate precision, recall, fscore across all classes
	m = d.shape
	c = m[0]
	r = m[1]

	for i in range (0, c):
		#true positive diagonal i, i
		tp = d[i][i]
		#false positive column i - tp
		fp =sum(d[:,i]) - d[i][i]
		#false negative row i - tp
		fn = sum(d[i,:]) - d[i][i]

		precision = tp / (tp + fp)
		recall = tp / (tp + fn)
		fscore = 2*(precision*recall / (precision + recall))
		info = 'class' + str(i+1) + ', ' + str(precision) + ', ' + str(recall) + ', ' + str(fscore)
		stats.append(info)

	if(save == 'yes'):
		tstamp = create_timestamp(location)
		fname = 'classifier_stats_' + confusion_matrix.split('.csv')[0] + '_' + tstamp + '.txt'
		stats_results = open(datapath + fname, 'w')
		stats_results.write('\n'.join(stats))
		stats_results.close()


	return(stats, fname)
# ------------------------------------------------------------------------------
# get the .tif sentinel2 file with the correct band 
def findband (band, token, ext, path):
	result = 'n.a.'
	files = os.listdir(path)
	for file in files:
		if((token in file) and (ext in file) and (band in file)):
			result = file
			break
		else:
			pass

	return(result)
#-------------------------------------------------------------------------------
def findband_roi(band, token, ext, path):
	result = 'n.a'
	area = 'roi'
	skip = '.xml'
	files = os.listdir(path)
	for file in files:
		if((token in file) and (ext in file) and (band in file) and (area in file) and not (skip in file)):
			result = file
			break
		else:
			pass
	return(result)
#-------------------------------------------------------------------------------
def get_minmax_points(path, rasterimage):
#https://stackoverflow.com/questions/2922532/obtain-latitude-and-longitude-from-a-geotiff-file

	ds = gdal.Open(path + rasterimage)
	width = ds.RasterXSize
	height = ds.RasterYSize
	gt = ds.GetGeoTransform()
	minx = gt[0]
	miny = gt[3] + width*gt[4] + height*gt[5]
	maxx = gt[0] + width*gt[1] + height*gt[2]
	maxy = gt[3]
	ds = None

	return(minx, miny, maxx, maxy)
#------------------------------------------------------------------------------
def get_minmax_points_multiple(path, rasterimages):
	minxs = []
	minys = []
	maxxs = []
	maxys = []

	for i in range(0, len(rasterimages)):
		ds = gdal.Open(path + rasterimages[i])
		width = ds.RasterXSize
		height = ds.RasterYSize
		gt = ds.GetGeoTransform()
		minx = gt[0]
		miny = gt[3] + width*gt[4] + height*gt[5]
		maxx = gt[0] + width*gt[1] + height*gt[2]
		maxy = gt[3]
		minxs.append(minx)
		minys.append(miny)
		maxxs.append(maxx)
		maxys.append(maxy)
		ds = None

	mminx = min(minxs)
	mminy = min(minys)
	mmaxx = min(maxxs)
	mmaxy = min(maxys)

	return(mminx, mminy, mmaxx, mmaxy)
#------------------------------------------------------------------------------

def zip_nopath (src, dst):
	zf = zipfile.ZipFile("%s.zip" % (dst), "w", zipfile.ZIP_DEFLATED)
	abs_src = os.path.abspath(src)
	for dirname, subdirs, files in os.walk(src):
		for filename in files:
			absname = os.path.abspath(os.path.join(dirname, filename))
			arcname = absname[len(abs_src) + 1:]
			print ('zipping %s as %s' % (os.path.join(dirname, filename),arcname))
			zf.write(absname, arcname)
	zf.close()
#-----------------------------------------------------------------------------

def send_to_pcloud(filelist, authfile, pclouddir):
	f = open(authfile, 'r')
	lines = f.readlines()
	username = lines[0].strip()
	password = lines[1].strip()
	f.close()

	conn = PyCloud(username, password, endpoint='nearest')
	conn.uploadfile(files=filelist, path=pclouddir)
	print('\n\nUploaded: ' , filelist)
#------------------------------------------------------------------------------
def check_image(image, threshold):
	c = Image.open(image)
	cg = c.convert("L")
	cga = numpy.array(cg)
	cgaf = cga.ravel()
	good  = cgaf[cgaf > threshold]
	percentage_good = int(100 * (len(good) / len(cgaf)))

	return(percentage_good)
#-----------------------------------------------------------------------------
def log(filename, comment, method):
	file = open(filename, method)
	value = file.write(comment)
	file.close()
#------------------------------------------------------------------------------
