# Project Setup

1. Create a new project directory:
   ```bash
   mkdir project
   cd project
   ```

## Step 1: Download Images and Labels

Run the `downloadImages.py` script to download images and labels into respective folders inside the project directory.

## Step 2: Write TFRecords to GCS

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
For now we haven't checked with any other patch size less than 8.


# Model Training

Run the training script after setting up the data.

To train model run `trainig.py` script.

```bash
python training.py --model_name <model_name.hdf5> --model_dir '<directory where to save the model>' --patch_size <patch_size: keep it 8 for now> --num_classes <number of classes> --epochs <epochs> --batch_size <batch_size>
```


Example to call for training.py
```bash
python training.py --model_name patch_8_batch_32_new_test.hdf5 --model_dir /home/jay/project/trained_models/test/ --patch_size 8 --num_classes 23 --epochs 3 --batch_size 64
```



# Prediction

To make predictions on images, use the `prediction.py` script.

```bash
python prediction.py --image_dir <images_dir>/ --choose '<number of images or all>' --output_dir <output directory where predictions are to be saved> --models_dir <directory to models to choose from>
```

Example:
```bash
python prediction.py --image_dir /home/jay/project/images/ --choose '2' --output_dir /home/jay/project/single_image/ --models_dir /home/jay/project/trained_models/
```

You will find the output in your mentioned output directory by the name of segmentation_mask.png, for now ignore plain_image.png

**Note:** The `--output_directory` is optional.


