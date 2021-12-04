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
from datetime import datetime
import pytz
import gdal
import otbApplication
import numpy

print('Testing OTB...\n\n')
print (str( otbApplication.Registry.GetAvailableApplications()))
