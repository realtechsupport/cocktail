# COCKTAIL
# settings_test.py
# check settings for your setup
# RTS, 2022
# -------------------------------------------------------------
import sys, os
import json
from datetime import datetime
import pytz
import gdal
import otbApplication
import numpy


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
