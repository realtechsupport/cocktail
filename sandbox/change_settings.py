import os, sys
import shutil

path = '/home/realtech/Desktop/'

#-----------------------------------------
def change_settings(infile, token1in, token2in, change, outfile):
    file = open(path + infile, 'r')
    inlines = file.readlines()
    i=0
    for line in inlines:
        i = i + 1
        if((token1in in line) and (token2in in line)):
            break

    inlines[i-1] =  '\t' + '"' + token1in + '" ' + ":" + ' "' + change + '"' + ',\n'
    file = open(path + outfile, 'w')
    file.writelines(inlines)
    file.close()

#----------------------------------------------

infile = "settings.txt"
orgfile = "settings_org.txt"
outfile = 'settings.txt'
token1in= "svm_k"
token2in = "linear"
token2out = ["polynomial", "gaussian", "notsure"]

#make backup
shutil.copyfile(path+infile, path+orgfile)

#make change based on list of token2out and run classifier after each change
for i in range (0, len(token2out)):
    change = token2out[i]
    change_settings(infile, token1in, token2in, change, outfile)
    infile = orgfile
    print('running classifier...', str(i))
