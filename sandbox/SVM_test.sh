# Test SVM repeatedly
# rts
# Jan 2022
#---------------------------------------------------------------------------
# call from the command line:
# sh SVM_test.sh libsvm
#---------------------------------------------------------------------------
echo "Starting SVM_test ... run the SVM algorithm 5 times with constant settings\n\n"

conda run -n OTB python3 /home/blc/gdal-otb-qgis-combo/code/otb_raster_classify.py "$1"
python3 /home/blc/gdal-otb-qgis-combo/code/delete_files.py

conda run -n OTB python3 /home/blc/gdal-otb-qgis-combo/code/otb_raster_classify.py  "$1"
python3 /home/blc/gdal-otb-qgis-combo/code/delete_files.py

conda run -n OTB python3 /home/blc/gdal-otb-qgis-combo/code/otb_raster_classify.py "$1"
python3 /home/blc/gdal-otb-qgis-combo/code/delete_files.py

conda run -n OTB python3 /home/blc/gdal-otb-qgis-combo/code/otb_raster_classify.py "$1"
python3 /home/blc/gdal-otb-qgis-combo/code/delete_files.py

conda run -n OTB python3 /home/blc/gdal-otb-qgis-combo/code/otb_raster_classify.py "$1"
python3 /home/blc/gdal-otb-qgis-combo/code/delete_files.py


echo "Process complete\n\n"
#---------------------------------------------------------------------------

