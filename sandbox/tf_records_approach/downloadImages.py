from google.cloud import storage
import os


def download_files_from_gcs(bucket_name, source_folder, destination_folder):
    client = storage.Client()

    # Get the bucket
    bucket = client.get_bucket(bucket_name)

    # List objects in the source folder
    blobs = bucket.list_blobs(prefix=source_folder)

    # Iterate through the blobs and download them
    for blob in blobs:
        if blob.name != source_folder:  # Avoid downloading the folder itself
            destination_path = f"{destination_folder}/{blob.name.replace(source_folder, '')}"
            
            # Check if file already exists locally
            if not os.path.exists(destination_path):
                blob.download_to_filename(destination_path)
                print(f"Downloaded: {blob.name}")
            else:
                print(f"Skipped (already exists): {blob.name}")




username = os.getenv("USER") or os.getenv("LOGNAME")


# # Replace these with your specific details
bucket_name = 'gislogics-bucket'
source_folder = 'area2_planetlabs_superdove/'
destination_folder = f'/home/{username}/project/images'

download_files_from_gcs(bucket_name, source_folder, destination_folder)



# Replace these with your specific details
label_bucket_name = 'tf_records_bucket'
label_source_folder = 'labels/'
label_destination_folder = f'/home/{username}/project/labels'

download_files_from_gcs(label_bucket_name, label_source_folder, label_destination_folder)