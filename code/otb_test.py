# COCKTAIL
# otb_test.py
# check installation of OTB - the Orfeo machine learning library
# RTS, 2022
# https://www.orfeo-toolbox.org/
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
