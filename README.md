# otb-qgis-combo

The Orfeo (OTB) machine learning library does not play well with QGIS outside of the and resource intensive GUI program.
The systems have differing and partially conflicting dependencies, and the GUI environment makes rapid testing across the various toolboxes integrated into QGIS very cumbersome and slow.
This repository shows you how to setup a virtual computer that can support OTB and QGIS functionality efficiently.

step 1 - VM
Create a virtual computer.
Choose Ubuntu 18.04 LTS

step 2 - install QGIS
Upload the batch file basics+qgis.sh
Make that file executable 
  chmod +x basics+qgis.sh
Run that file 
  sh basics+qgis.sh

step 3 - install OTB in a virtual environment with conda
Upload the batchfile conda-packages.sh and the context file environment.yml
Make that file executable
  chmod +x conda-packages.sh
Run that file 
  sh conda-packages.sh

step 4 - personalize
Add other libraries to the OTB environment as needed
	conda install -c conda-forge pillow
	conda install -c conda-forge geopandas
  
step 5 - test the setup
Run qgis_test in the base environment 
  python3 qgis_test.py
Activate the OTB environment 
  conda activate OTB
Run the otb_test
  python3 otb_test.py
  
You can now use QGIS in the base installation and enable the conda environment to access OTB functionality
You can cross-access libraries from either environment with python scripts for each of the environments:

  echo "Starting OTB-QGIS pipeline...\n\n"
  conda run -n OTB python3 /home/code/otb_code_A.py
  python3 /home/code/qgis_code_A.py
  conda run -n OTB python3 /home/code/otb_code_B.py
  python3 /home/code/qgis_code_B.py

  echo "Process complete"
  
 Since the directory structure you setup will be identical to the QGIS and OTB environments, intermediate filed produced will be available to processes running in either environment.



  
 


