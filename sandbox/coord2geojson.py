# coord2geojson.py
#
# Generate geojson conform information from field notes.
# Latitude [north or south]. Longitude [east or west] and land use category in English and Bahasa, and comments. 
# Example: -8.123, 115.123, urban_dwelling, pemukiman, hard to reach area
# Assumes elements are comma separated with one entry per line.
# No trailing new lines at the end of the last line of the input file, please..
# Jan 2022
# RTS
#----------------------------------------------------------------------------
# given the following categories for area2 (Tamblingan)
# 1 danau (water)
# 2 pemukiman (urban dwelling)
# 3 semak belukar (shrubs)
# 4 rerumputan (grass)
# 5 hutan homogen (homogeneous forest)
# 6 hutan campuran (mixed forest)
# 7 lahan pertanian {kampung agriculture)
# 8 lahan terbuka (open area)
# 9 kebun campuran(mixed garden)
#----------------------------------------------------------------------------

import os, sys
from geojson import dump, Polygon, Point, Feature, FeatureCollection

#set to true if your output requires Lat first, Long second
#set to false if your output requires Long first,  Lat second
Lat_Long_output = False

#set to true if you want to use Bahasa categories
#set to false if you want to use English categories
Bahasa_categories = True

# datapaths, inputs and outputs
datapath = '/home/blc/gdal-otb-qgis-combo/data/'
inputfilename = 'test_coordinates.txt'
outputfilename = 'geojson_' + inputfilename.split('.')[0] + '.geojson'

# dictionaries with set categories
area2_cats_english = {'water':1, 'urban_dwelling':2, 'shrubs':3, 'grass':4, 'homogeneous_forest':5, 'mixed_forest':6, 'kampung_agriculture':7, 'open_area':8, 'mixed_garden':9}
area2_cats_bahasa = {'danau':1, 'pemukiman':2, 'semak_belukar':3, 'rerumputan':4, 'hutan_homogen':5, 'hutan_campuran':6, 'lahan_pertanian':7, 'lahan_terbuka':8, 'kebun_campuran':9}

features_list = []
f = open(datapath+inputfilename)
# for each item in the list, create features with coordinates and class, add to list and then to FeatureCollection
for item in f:
	elements = []
	elements = item.split(',')

	if(Lat_Long_output):
		P = Point((float(elements[0]), float(elements[1])))
	else:
		P = Point((float(elements[1]), float(elements[0])))

	try:
		if(Bahasa_categories):
			k = elements[3].strip()
			v = area2_cats_bahasa[k]
		else:
			k = elements[2].strip()
			v = area2_cats_english[k]
	except:
		k = 'error'
		v = -1
	try:
		c = elements[4].strip()
	except:
		c = 'empty'

	F = Feature(geometry = P, properties={"class":v, "name":k, "comment":c})
	features_list.append(F)

feature_collection = FeatureCollection(features_list)
print('\nHere is the feature collection: \n')
print(feature_collection)

# save as geojson file
with open(datapath + outputfilename, 'w') as ff:
   dump(feature_collection, ff)
#----------------------------------------------------------------------------
