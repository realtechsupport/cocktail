# COCKTAIL
# settings_check.py
# Find the last modification date of the settings file
# November 2022

import sys, os
import json
from helper import *

# Local path and variables
datapath = '/home/ghemanth2578/cocktaildata/'
inputsfile = datapath + 'settings.txt'

mod_time = time.ctime(os.path.getmtime(inputsfile)) + ' UTC'
print('\n > Settings last updated on: ', mod_time)
print()
