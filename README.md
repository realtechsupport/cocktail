## Cocktail 

<i> Resource constrained, collaborative satellite asset collection and analysis </i>
<br><br>

<p align="center">
  <img src="https://github.com/realtechsupport/cocktail/blob/main/imgs/tip+cue4.png?raw=true" alt="cocktail tip and cue"/>
</p>

Cocktail is designed to facilitate resource constrained collaborative inquiry on optical satellite assets. Resource constrained collaboration is supported in several different ways. Cocktail will vary parameters of a classifier in batch mode and store the classifier performances for each setting so you can collaboratively can find the best configuration. Cocktail keeps track of the large collection of parameters across the individual processing modules in a single file such that remote collaborators can reliably replicate a workflow. Moreover, Cocktail can be linked with an external cloud storage provider to move assets out of the compute environment for low-cost storage of large GIS files. 

Cocktail is designed as a compendium to other GIS investigation environments, combines GDAL. OTB and GQIS elements, and is intened to be deployed remotely. The combination requires some attention. The [Orfeo](https://www.orfeo-toolbox.org/tag/machine-learning/) machine learning library and the translator library for raster and vector geospatial data formats [GDAL](https://gdal.org/) do not play well with the open source geographic information system [QGIS](https://qgis.org) outside of a resource intensive GUI environment.  Cocktail allows you to setup a low-cost virtual computer to apply several different classifiers including vector support machines, random forests, neural networks and various bandmath operations across GDAL, OTB and QGIS.

Private sector, high-resolution, daily-updated satellite assets have become a significant resource for remote sensing operations. A case in point is PlanetScope (PS), currently operating the largest collection of small Earth-imaging satellites. Cocktail facilitates the combination of free and commercial satellite assets to monitor  an area of interest with a low cost system, and then switches to a high resolution asset only if a condition of concern or interest has been detected and not adequately understood in the first data set. Not unlike the tip and cue concept in which one monitors an area of interest with one sensor and then ‘tips’ another complementary sensor platform to acquire another image over the same area, Cocktail tips and cues based on economic constraints.<br><br>

Check the Install+Use.pdf document for details and examples.
<br><br>
Here is a brief description of the steps required to get started:

1 - VM <br>
Create a virtual computer. Choose Ubuntu 18.04 LTS, with at least 16GB of RAM. If you intend on working with Sentinel data from ESA, it can be beneficial to build a VM close to ESA in Frankfurt. <br>

2- Get the repo files from this Github site. <br>
You will have all the files in the correct directory structure on your computer after the download. <br>

3 - Install QGIS. <br>
Go to the setup folder. Make the file basics+qgis.sh executable.<br>

  	chmod +x basics+qgis.sh
	
Run that file. <br>

  	sh basics+qgis.sh

4 - Install OTB in a virtual environment with conda. <br>
Go to the setup folder. Make the file conda-packages.sh executable. <br>

  	chmod +x conda-packages.sh
	
Run that file. <br>

  	sh conda-packages.sh
	
5 - Create a conda environment with defined dependencies.<br>
(OTB 7.2 requires python 3.7, for example.)

	conda env create -f environment.yml
	

6 - Customize <br>
Add other libraries to the OTB environment as needed. Enable the OTB environment to install geojson and geopandas. The geopandas install may take a bit of time. <br>

	conda install -c conda-forge pillow
	conda install -c conda-forge geojson
	conda install -c conda-forge geopandas
	conda install -c conda-forge sentinelsat

	
7 – Setup the directory structure <br>
The directories code, data, results should be ready made in your repository directory.
Put the rasterimages and vectorfiles directories into the data directory. Place image assets (.tif) in the rasterimages directory and vector assets (.shp) into the vectorfiles directory. Add the corresponding .dbf, .prj, .shx files for each .shp file.

Use the settings.txt file (in the data directory) to set your file names, process preferences and classification parameters. The content of this file is parsed and passed to the classification steps.

  
8 - Test<br>
a) Test QGIS

Run the qgis test in the base environment <br>

  	python3 qgis_test.py
	

b) Test OTB

Activate the OTB environment <br>

  	conda activate OTB
	
Run the otb test <br>

  	python3 otb_test.py
  
You can now use QGIS in the base installation and enable the conda environment to access OTB functionality. 
You can also move across environments to access libraries from either environment with python scripts as outlined below (see vector_classify_top.sh): <br>

  	echo "Starting OTB-QGIS pipeline...\n\n" 
  	conda run -n OTB python3 /home/code/otb_code_A.py 
  	python3 /home/code/qgis_code_A.py 
  	conda run -n OTB python3 /home/code/otb_code_B.py 
  	python3 /home/code/qgis_code_B.py 
	 
	 
Since the directory structure you setup will be identical in both the QGIS and OTB environments, intermediate filed produced will be available to processes running in either environment, allowing for data to be shared. All settings across the script modules are stored in the 'settings.txt' resource file and imported to the individual modules.

<i>Details on how to collect data from the European Space Agency's Sentinel program, how to make use of tip and cue, and how to perform various band-math operations and image classification with SVM, RF and NN classifiers is described in the Install+Use .pdf document.</i>

The sandbox folder contains some experiments. For example, a script to convert field notes in GPS data and land categories into geojson conform datasets. The file text_coordinates is a sample input and the file geojson_test_coordinates.geojson is the output generated by the script coord2geojson.py.


Cocktail is currently supporting the following research projects:

[Who speaks for the forest? Participatory mapping and contested land cover classification in Central Bali - FOSS4G2022](https://talks.osgeo.org/foss4g-2022-academic-track/talk/33PMHD/) <br>
[Combining Landsat, Sentinel2 and Planet Lab satellite assets for resource constrained land cover analysis in the tropics - EUROCARTO2022](https://eurocarto2022.org/accepted-submissions/)


