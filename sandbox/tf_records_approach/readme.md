> mkdir project
> cd project

## Step 1 Run the downloadImages.py script
This will download the images in and labels in respective folder inside project directory.



## Step 2 Run the script write_tf_records.py

### How to run the script write tf_records.py
>> python write_tf_records.py --bucket_name <BUCKET_NAME>

### Example to run the script write_tf_records.py
>> python write_tf_records.py --bucket_name tf_records_bucket

This would most probably will give an error rising from google storage [Error 403] indicating either not proper permission acquired for the storage or it doesn't exist.

#### How to solve this?
>>>> Create a new bucket (keep the same name in script's bucket_name)

Run this in CLI:
>>>> gcloud init

follow this link [How to initialize the google for granting access to write TF_Records in Bucket] https://cloud.google.com/sdk/docs/initializing

This will print some configuration and projects, choose those. 
After granting proper access tf_records will be written to that bucket in dir tf_records/









## Before training if, you want to change any paramater related to patches, please change those parameters in create_dataset.py script













### How to call prediction:
python prediction.py <images_dir>/ '<number of images or all>' -- output_directory <output directory where prediction are to saved>

>> -- output_directory is not necessary.

### Example for prediction.py
python prediction.py /home/jay/project/images/ '2' --output_directory /home/jay/project/single_image/

