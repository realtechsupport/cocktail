# COCKTAIL
# adjust_datapaths.py
# ------------------------------------------------------------------------------
# Adjust paths in the settings file and scripts to match your configuration.
# RTS, JULY 2022
#-------------------------------------------------------------------------------
import os, sys, json

#-------------------------------------------------------------------------------
def main():
    #old_path = '/home/blc/cocktail/'
    old_path = '/home/marcbohlen/cocktail/'
    current_path = os.getcwd()
    new_path = current_path.split('setup')[0]
    scripts_path = new_path + 'code/'

    old_settings = new_path + 'data/settings.txt'
    new_settings = new_path + 'data/new_settings.txt'

    print('\nUse this script to adjust paths in the settings file and scripts to match your configuration.')
    print('Run this script only once after installing (or updating) COCKTAIL.')
    print('Here is the default old path: ', old_path)

    input_path = input('\nEnter an alternate old path to the COCKTAIL directory or hit any key to use the default path: ')

    if(len(input_path) > 1):
        old_path = input_path
        print('\nUsing the selected path: ', old_path)
    else:
        print('\nDefaulting to this old path: ', old_path)


    update_settings (old_settings, new_settings, old_path, new_path)
    check_settings (old_settings)
    update_scripts(scripts_path, old_path, new_path)

# ------------------------------------------------------------------------------
def update_settings (old_settings, new_settings, old_path, new_path):
    #Search the complete file and update the paths
    with open(old_settings, "rt") as fin:
        with open(new_settings, "wt") as fout:
            for line in fin:
                fout.write(line.replace(old_path, new_path))

#               rename the updated file to settings.txt
    os.rename(new_settings, old_settings)
    print('\nSettings file updated.')

#-------------------------------------------------------------------------------
def check_settings (old_settings):
    #show all the variables
    try:
        f = open(old_settings, 'r')
        data = f.read()
        #print(data)
        jdata = json.loads(data)
        f.close()
    except:
        print('\n...data access error...\n')
    else:
        print('\nHere are the settings parameters:\n\n')
        print(jdata)
        print('\n\n')

#-------------------------------------------------------------------------------
def update_scripts(scripts_path, old_path, new_path):
    #get all the scripts
    scripts = [script for script in os.listdir(scripts_path)]
    #replace old path with new path in each script
    for script in scripts:
        #print(script)
        new_script = 'new_' + script
        #print(new_script)
        with open(scripts_path + script, "rt") as fin:
            with open(scripts_path + new_script, "wt") as fout:
                for line in fin:
                    fout.write(line.replace(old_path, new_path))

        os.rename(scripts_path + new_script, scripts_path + script)
        print('Updated: ', script)

    print('\nAll scripts updated.')

#-------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
#-------------------------------------------------------------------------------
