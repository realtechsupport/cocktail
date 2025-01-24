#!/bin/bash
# type sudo chmod 774 condapackages1.sh at the command line to make the script executable
# type "./conda-packages1.sh" at the command line to launch this script
# RTS, sept 2019, oct 2021
# update Jan 2025
#-------------------------------------------
clear
echo "WELCOME - conda package installer "
echo "This utility will install additional conda packages to your home directory"
mkdir code
mkdir data
mkdir results
sudo apt-get update
sudo apt-get upgrade
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh ./Miniconda3-latest-Linux-x86_64.sh

echo
echo "installed conda on your system"
echo "close this window, restart a new SSH session"

echo 'export PATH="$PATH:/home/ghemanth2578/miniconda3/bin/"' >> ~/.bashrc
source ~/.bashrc

echo
echo "hit ctrl d to close this session"
exit 0
#end this part by closing the terminal and lanuching a new SSH session
