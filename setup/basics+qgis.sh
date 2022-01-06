#!/bin/bash
# setup basics for QGIS linux VM
# type sudo chmod 774 azure_basics.sh at the command line to make the script executable
# type " sh azure_basics.sh" at the command line to launch this script
# RTS, may 2020
#-------------------------------------------
clear
echo "WELCOME - basics for the GCP install "

sudo apt-get update
sudo apt-get upgrade -y

sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
sudo apt-get install qgis otb-bin monteverdi saga -y

sudo apt-get install python3-dev -y
sudo apt-get install build-essential python3-dev -y
sudo apt-get install python3-venv -y

sudo apt-get install ffmpeg -y
sudo apt install jupyter-notebook -y

pip3 install --upgrade pip
pip3 install --upgrade pillow

pip3 install numpy
pip3 install matplotlib
pip3 install pandas
pip3 install scipy

echo "installed python3, python3dev, python3-venv, ffmpeg, sox, qgi, numpy, scipy, matplotlib, jupyter notebook"

echo "hit ctrl d to close this session"
exit 0
#end this part by closing the terminal and lanuching a new SSH session
