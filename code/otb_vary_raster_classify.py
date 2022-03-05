# vary_raster_classify.py
# helper file to evaluate different hyperparameters for SVM and RF classifiers
# changes the parameters in "setings.txt" and then runs "otb_raster_classify"
# for each combination of those parameters, and saves output images and settings to VM
# get token names and defaul values from the settings file.
# enable the OTB environment before you run this (conda activate OTB)
# RTS, march 2022
#----------------------------------------------------------------------------
import os, sys
import shutil, time
import subprocess
from helper import *
#----------------------------------------------------------------------------
datapath = '/home/blc/cocktail/data/'
codepath = '/home/blc/cocktail/code/'
settingsname = "settings.txt"
orgfile = "settings_org.txt"
infile = settingsname
outfile = infile

# set the the classifier to call
program = 'otb_raster_classify.py'
choice  =  'SVM'

#-----------------------------------------------------------------------------
if (choice == 'SVM'):
	selection = 'libsvm'
	#parameter names to vary
	token1_name = "svm_k"
	token2_name = "svm_c"
	#default values
	token1_value = "linear"
	token2_value = "1"

	#leave unchanged ... token1_list = ["linear"]
	#OR multiple values [a,b,c]

	#SVM: linear/rbf/poly/sigmoid
	token1_list = ['rbf', 'poly']
	#0.1 ... 1.0
	token2_list = ["0.7", "0.4"]

elif (choice == 'RF'):
	#"rf_max" : "5", "rf_min" : "1",
	#"rf_ra" : "0", "rf_cat" : "10",
	#"rf_var" : "0", "rf_ntrees" : "100",
	#"rf_acc" : "0.01"

	selection =  'rf'
	token1_name = 'rf_ntrees'
	token2_name = 'rf_min'
	token1_value = '100'		#get these from the current setting file
	token2_value = '1'
	token1_list = ['300', '1000']
	token2_list = ['3', '5']

else:
	print('Check the choice...')
	sys.exit()

#-----------------------------------------------------------------------------

#make backup of settings file
shutil.copyfile(datapath+infile, datapath+orgfile)

#run classifier with default settings.
try:
	print('\n\nrunning classifier with settings..DEFAULT\n\n')
	command = 'python3 ' + codepath + program + ' ' + selection
	os.system(command)
except:
	print('\nError running classifier...')

#make change based on list of token1_list, token2_list and run classifier after each change
for i in range (0, len(token1_list)):
	for j in range (0, len(token2_list)):
		change1 = token1_list[i]
		change2 = token2_list[j]
		change_settings(datapath, infile, token1_name, token1_value, token2_name, token2_value, change1, change2, outfile)
		#use the origininal settings as reference again
		infile = orgfile
		try:
			print('\n\nrunning classifier with settings..', i,j, change1, change2)
			command = 'python3 ' + codepath + program + ' ' + selection
			os.system(command)
			#wait one minute
			print('\n\n Waiting for 2 minutes...')
			time.sleep(120)
		except:
			print('\nError running classifier...')
			break

print("RESETTING input file to start position")
os.remove(datapath+outfile)
os.rename(datapath+orgfile, datapath+settingsname)

#---------------------------------------------------------------------------------

