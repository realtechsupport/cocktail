import os, sys
from geojson import Polygon, Point, Feature

filepath = '/home/blc/gdal-otb-qgis-combo/data/'
filename = 'test_coordinates.txt'

list = []

f = open(filepath+filename)
for item in f:
	elements = []
	elements = item.split(',')
	#for e in elements:
	#	print(e)
	P = Point((float(elements[0]), float(elements[1])))
	F = Feature(geometry = P, properties={"class":elements[2].strip('\n')})
	print(F)
