# -*- coding: utf-8 -*-
# helper.py
# routines to support the OTB-QGIS toolchain
# RTS, Jan 2022
# ------------------------------------------------------------------------------
import os, sys, numpy
#-------------------------------------------------------------------------------
# Precision, Recall and Fscore gleaned from a multi-class confusion matrix
# https://en.wikipedia.org/wiki/Precision_and_recall
def get_classifier_statistics(datapath, confusion_matrix, save):
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
		fname = 'classifier_stats_' + confusion_matrix.split('.csv')[0] + '.txt'
		stats_results = open(datapath + fname, 'w')
		stats_results.write('\n'.join(stats))
		stats_results.close()

	return(stats)
# ------------------------------------------------------------------------------
