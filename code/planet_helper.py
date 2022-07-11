# COCKTAIL
# planet_helper.py
# utilities to assist with downloading planet lab imagery via API V1
# RTS, spring 2021 / 2022
#-------------------------------------------------------------------------------
import os, sys, json, requests
import time
import json
from requests.auth import HTTPBasicAuth

#-------------------------------------------------------------------------------
def pl_download(url, datapath, PLANET_API_KEY, filename=None):
	# download asset files
	# url (the location url), -filename (the filename to save it as. defaults to whatever the file is called originally)
    # Send a GET request to the provided location url, using your API Key for authentication
    res = requests.get(url, stream=True, auth=(PLANET_API_KEY, ""))
    # If no filename argument is given
    if not filename:
        # Construct a filename from the API response
        if "content-disposition" in res.headers:
            filename = res.headers["content-disposition"].split("filename=")[-1].strip("'\"")
        # Construct a filename from the location url
        else:
            filename = url.split("=")[1][:10]
    # Save the file
    with open(datapath + filename, "wb") as f:
        for chunk in res.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    print('download complete...')
    return (filename)

#-------------------------------------------------------------------------------
def getasset(self_link, datapath, maxattempts, wait, PLANET_API_KEY):
# get a specific asset; try max times and wait between attempts

  for attempt in range (1, maxattempts):
    activation_status_result = requests.get(self_link, auth=HTTPBasicAuth(PLANET_API_KEY, ''))
    activation_status = activation_status_result.json()["status"]
    print('number of access attempts and activation status: ', attempt, activation_status)

    if(activation_status == 'active'):
      download_link = activation_status_result.json()["location"]
      print('downloading the asset...')
      asset = pl_download(download_link, datapath, PLANET_API_KEY);
      print('saved this file to the datapath: ', asset)
      break
    elif(activation_status == 'activating'):
      print('asset not ready yet... retrying in 1 minute')
      time.sleep(wait)
    else:
      print('unknown asset request error occurred...')
      break
#-------------------------------------------------------------------------------
