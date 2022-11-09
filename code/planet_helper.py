# COCKTAIL
# planet_helper.py
# utilities to assist with downloading planet lab imagery via API V1
# RTS, spring 2021 / 2022
#-------------------------------------------------------------------------------
import os, sys, json, requests
import shutil
import time
import json
import pathlib
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
def place_order(request, auth, orders_url, headers):
    response = requests.post(orders_url, data=json.dumps(request), auth=auth, headers=headers)
    print(response)

    if not response.ok:
        raise Exception(response.content)

    order_id = response.json()['id']
    print(order_id)
    order_url = orders_url + '/' + order_id
    return (order_url)
#-------------------------------------------------------------------------------

def poll_for_success(order_url, auth, num_loops):
    count = 0
    while(count < num_loops):
        count += 1
        r = requests.get(order_url, auth=auth)
        response = r.json()
        state = response['state']
        print(state, count)
        success_states = ['success', 'partial']
        if state == 'failed':
            raise Exception(response)
        elif state in success_states:
            break

        time.sleep(10)
#-------------------------------------------------------------------------------

def download_order(savepath, order_url, auth, overwrite=False):
	r = requests.get(order_url, auth=auth)
	print(r)
	
	response = r.json()
	results = response['_links']['results']
	results_urls = [r['location'] for r in results]
	results_names = [r['name'] for r in results]
	results_paths = [pathlib.Path(os.path.join(savepath, n)) for n in results_names]
	print('{} items to download'.format(len(results_urls)))

	for url, name, path in zip(results_urls, results_names, results_paths):
		if overwrite or not path.exists():
			print('downloading {} to {}'.format(name, path))
			r = requests.get(url, allow_redirects=True)
			path.parent.mkdir(parents=True, exist_ok=True)
			open(path, 'wb').write(r.content)
		else:
			print('{} already exists, skipping {}'.format(path, name))

	return (dict(zip(results_names, results_paths)))
#-------------------------------------------------------------------------------
