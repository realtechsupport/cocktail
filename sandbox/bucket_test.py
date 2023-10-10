import sys, os
from google.cloud import storage
#rts, october 2023
#-------------------------------------------
def list_items(bucket_name):
    """Lists all the items in the GCP bucket."""
    storage_client = storage.Client()
    items = storage_client.list_blobs(bucket_name)
    for item in items:
        print(item.name)
#-------------------------------------------

bucket_name = 'gislogics-bucket'
list_items(bucket_name)
