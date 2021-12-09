# ORFEO Toolbox
# classifier training and image classification
# classifiers: Support Vector Machine, Random Forest, Artificial Neural Net
# color map
# transport to pCloud
# install on Ubuntu 18 LTS with conda (conda-packages1.sh and environmentv1.yml.)
# RTS, Nov 2021

# +++
#http://wiki.awf.forst.uni-goettingen.de/wiki/index.php/Object-based_classification_(Tutorial)
#https://www.orfeo-toolbox.org/CookBook/recipes/pbclassif.html?highlight=attributes
# +++
# -------------------------------------------------------------
import sys, os
import json
from datetime import datetime
import pytz
import gdal
import otbApplication
import numpy

print('Testing OTB...\n\n')
print (str( otbApplication.Registry.GetAvailableApplications()))

print('Checking the settings\n')
datapath = '/home/marcbohlen/data/'
inputsfile = datapath + 'settings.txt'

#collect the variables
try:
        f = open(inputsfile, 'r')
        data = f.read()
        jdata = json.loads(data)
        f.close()
except:
        print('\n...data access error...\n')
else:
        print('\nHere are the settings parameters:\n\n')
        print(jdata)
