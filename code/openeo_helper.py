# openeo_helper.py
# Dec 2024, RTS

import openeo

def initialize(url="openeo.dataspace.copernicus.eu"):
  connection = openeo.connect(url=url)
  connection.authenticate_oidc()
  return connection


def create_job(connection,bbox,start,end,satellite, band_selection, max_cloud,job_title="testing"):
	cube = connection.load_collection(
	satellite,
	spatial_extent = {"west": min(bbox[2],bbox[0]), "south": min(bbox[3],bbox[1]),"east": max(bbox[0],bbox[2]),"north": max(bbox[3],bbox[1])},
	temporal_extent = [start, end],
	bands = band_selection,
	max_cloud_cover = max_cloud,
	)
	cube = cube.save_result(format="GTiff")
	job = cube.create_job(title = job_title)
	
	return (job)
