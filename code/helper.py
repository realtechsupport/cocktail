# -*- coding: utf-8 -*-
# helper.py
# routines to support the OTB-QGIS toolchain COCKTAIL
# RTS, Jan/April 2022
# ------------------------------------------------------------------------------
import os, sys, numpy
from datetime import datetime
import pytz
import glob, shutil, zipfile
from zipfile import ZipFile

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
