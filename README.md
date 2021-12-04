# otb-qgis-combo

The Orfeo (OTB) machine learning library does not play well with QGIS outside of the resource intensive GUI program.
The systems have differing and partially conflicting dependencies, and the GUI environment makes rapid testing across the various tool boxes cumbersome and slow.
This repository shows you how to setup a virtual computer that can support OTB and QGIS functionality efficiently.

step 1 - VM <br>
Create a virtual computer.<br>
Choose Ubuntu 18.04 LTS <br>

step 2 - install QGIS <br>
Upload the batch file basics+qgis.sh <br>
Make that file executable  <br>

  	chmod +x basics+qgis.sh
Run that file <br>

  	sh basics+qgis.sh

step 3 - install OTB in a virtual environment with conda <br>
Upload the batchfile conda-packages.sh and the context file environment.yml <br>
Make that file executable <br>

  	chmod +x conda-packages.sh
Run that file <br>

  	sh conda-packages.sh

step 4 - personalize <br>
Add other libraries to the OTB environment as needed <br>

	conda install -c conda-forge pillow
	
	conda install -c conda-forge geopandas
  
step 5 - test the setup <br>
Run qgis_test in the base environment <br>

  	python3 qgis_test.py
	
Activate the OTB environment <br>

  	conda activate OTB
	
Run the otb_test <br>

  	python3 otb_test.py
  
You can now use QGIS in the base installation and enable the conda environment to access OTB functionality. 
You can cross-access libraries from either environment with python scripts for each of the environments: <br>

  	echo "Starting OTB-QGIS pipeline...\n\n" 
	
  	conda run -n OTB python3 /home/code/otb_code_A.py 
	
  	python3 /home/code/qgis_code_A.py 
	
  	conda run -n OTB python3 /home/code/otb_code_B.py 
	
  	python3 /home/code/qgis_code_B.py 
	
 	echo "Process complete"
	 
  
Since the directory structure you setup will be identical to the QGIS and OTB environments, intermediate filed produced will be available to processes running in either environment.



  
 


