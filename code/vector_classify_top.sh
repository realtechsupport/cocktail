# COCKTAIL
# object_classify_top.sh
# top level script to perform neural network based object classification
# on a rasterimage together with a vector based point file
# script access functionality across Orfeo and Qgis libraries sequentially
# RTS, February, September 2022
#---------------------------------------------------------------------------
# uncomment commands to run tests
# OTB
# conda run -n OTB python3 /home/marcbohlen/code/tests/OTB_test.py
# QGIS
# python3 /home/marcbohlen/code/tests/qgis_test.py
#---------------------------------------------------------------------------
# OTB and QGIS sequence for vector based classification (ANN)

# 1 OTB_part1 (otb_vector_classify_1)
# 2 QGIS_join
# 3 OTB_part2 (otb_vector_classify_2)
# 4 QGIS_render

# raster and vector data defined in the settings.txt file
#---------------------------------------------------------------------------
echo "\nStarting the object based Neural Net Classifier."
echo "Check the settings.txt file for all inputs and hyperparameters."
echo "Press any key when you are ready... or Ctrl c to exit..."
read var

echo "\nThis process will take several minutes (32GB RAM) or about half an hour (8GB RAM)"
echo "Proceeding with the classification"
conda run -n OTB python3 /home/marcbohlen/cocktail/code/otb_vector_classify_1.py
python3 /home/marcbohlen/cocktail/code/qgis_join.py
conda run -n OTB python3 /home/marcbohlen/cocktail/code/otb_vector_classify_2.py
python3 /home/marcbohlen/cocktail/code/qgis_render.py

echo "\n\nNEURAL NET CLASSIFICATION - process complete\n\n"
#---------------------------------------------------------------------------
