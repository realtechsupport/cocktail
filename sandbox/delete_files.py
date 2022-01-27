import sys, os, glob, shutil, zipfile
import time

print("...waiting 60 seconds ...")
time.sleep(60)

#delete ---------------------------------------------------
vp = '/home/blc/gdal-otb-qgis-combo/data/vectorfiles/' + '*.*'
files = glob.glob(vp)
for file in files:
  os.remove(file)

rp = '/home/blc/gdal-otb-qgis-combo/results/' + '*.*'
files = glob.glob(rp)
for file in files:
  os.remove(file)


#repopulate ------------------------------------------------
p = '/home/blc/gdal-otb-qgis-combo/data/'
#f1 = 'area1_vector_classification_GVM.zip'
#f2 = 'area1_0612_2020_raster_classification.zip'
f1 = 'area2_0612_2020_vector_classification.zip'
f2 = 'area2_0612_2020_raster_classification.zip'


shutil.copy(p + 'collection/'+ f1, p + 'vectorfiles/' + f1)
shutil.copy(p + 'collection/'+ f2, p + 'vectorfiles/' + f2)

with zipfile.ZipFile(p +'vectorfiles/' + f1, 'r') as zip_ref:
  zip_ref.extractall(p +'vectorfiles/')

with zipfile.ZipFile(p +'vectorfiles/' + f2, 'r') as zip_ref:
  zip_ref.extractall(p +'vectorfiles/')
