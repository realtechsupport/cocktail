#!/bin/bash
# first of two bash files to install conda packages
# type sudo chmod 774 condapackages1.sh at the command line to make the script executable
# type "./conda-packages1.sh" at the command line to launch this script
# RTS, sept 2019, oct 2021
#-------------------------------------------
clear
echo "WELCOME - conda package installer, part 1 "
echo "This utility will install additional conda packages to your home directory"
mkdir code
mkdir data
sudo apt-get update
sudo apt-get upgrade
wget https://repo.anaconda.com/miniconda/Miniconda2-latest-Linux-x86_64.sh
sh ./Miniconda2-latest-Linux-x86_64.sh

echo
echo "installed conda on your system"
echo "close this window, restart a new SSH session"
echo "run the second package installer conda-packages2.sh"

source ~/.bashrc

echo
echo "hit ctrl d to close this session"
exit 0
#end this part by closing the terminal and lanuching a new SSH session
