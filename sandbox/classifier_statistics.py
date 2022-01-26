# -*- coding: utf-8 -*-
"""classifier_statistics.py

# Precision, Recall and Fscore gleaned from a multi-class confusion matrix
# RTS, Jan 2022
# https://en.wikipedia.org/wiki/Precision_and_recall

#usage:
# Select the multi-class confusion matrix already created by the classifier
    confusion_matrix = 'confusionmatrix_svm.csv'
# Generate the statistics (include path to the file)
    svm_stats = get_classifier_statistics(datapath, confusion_matrix)
    for result in svm_stats:
        print (result)
"""
#-------------------------------------------------------------------------------
import os, sys, numpy
#------------------------------------------------------------------------------
def get_classifier_statistics(datapath, confusion_matrix):
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

  return(stats)
#-------------------------------------------------------------------------------
