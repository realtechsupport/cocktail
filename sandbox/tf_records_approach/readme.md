# Project Setup

1. Create a new project directory:
   ```bash
   mkdir project
   cd project
   ```

## Step 1: Download Images and Labels

Run the `downloadImages.py` script to download images and labels into respective folders inside the project directory.

## Step 2: Generate TF Records

### Run the script `write_tf_records.py`

Use the following command to execute the script:
```bash
python write_tf_records.py --bucket_name <BUCKET_NAME>
```

Example:
```bash
python write_tf_records.py --bucket_name tf_records_bucket
```

**Note:** You may encounter a Google Storage error [Error 403]. This indicates a permission issue or the bucket not existing.

#### Troubleshooting:

1. **Create a New Bucket:**
   If the error persists, create a new bucket with the same name as in the script's `bucket_name`.

2. **Grant Proper Access:**
   Run the following command to initialize Google Cloud and grant proper access:
   ```bash
   gcloud init
   ```
   Follow [this link](https://cloud.google.com/sdk/docs/initializing) for detailed instructions. Choose the displayed configuration and projects.

   After granting access, TF Records will be written to the specified bucket in the `tf_records/` directory.

## Before Training

If you want to modify any parameters related to patches, make changes in the `create_dataset.py` script.

# Model Training

Run the training script after setting up the data.

# Prediction

To make predictions on images, use the `prediction.py` script.

```bash
python prediction.py <images_dir>/ '<number of images or all>' --output_directory <output directory where predictions are to be saved>
```

Example:
```bash
python prediction.py /home/jay/project/images/ '2' --output_directory /home/jay/project/single_image/
```

**Note:** The `--output_directory` is optional.


