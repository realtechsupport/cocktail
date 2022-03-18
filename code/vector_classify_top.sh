#top level script to run OTB, GDAL and QGIS scripts sequentially
#rts
#december 2021
#---------------------------------------------------------------------------
#uncomment commands to run tests
#OTB
#conda run -n OTB python3 /home/marcbohlen/code/tests/OTB_test.py
#QGIS
#python3 /home/marcbohlen/code/tests/qgis_test.py
#---------------------------------------------------------------------------
# OTB and QGIS sequence for vector based classification (ANN)

# 1 OTB_part1 (otb_vector_classify_1)
# 2 QGIS_join
# 3 OTB_part2 (otb_vector_classify_2)
# 4 QGIS_render

#---------------------------------------------------------------------------
echo "Starting OTB-GDAL-QGIS pipeline...\n\n"

conda run -n OTB python3 /home/blc/cocktail/code/otb_vector_classify_1.py
python3 /home/blc/cocktail/code/qgis_join.py
conda run -n OTB python3 /home/blc/cocktail/code/otb_vector_classify_2.py
python3 /home/blc/cocktail/code/qgis_render.py
 
echo "Process complete\n\n"
#---------------------------------------------------------------------------
