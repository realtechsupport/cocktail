# Multi Image Model

## Instructions

1. Create folders named `images` and `roi_folder` inside the `all/data` folder.

2. Copy the image tiff files into the `images` folder (e.g., `area2_0516_2023_composite.tif`, `area2_0529_2023_composite.tif`, etc).

3. Copy the shape file into the `roi_folder` (e.g., `area2_square.geojson`).

4. Copy the `crop_mask.tif` (mask file) into the `all/data` folder (not into the `images` folder).

5. Copy the new code files into the `all/code` folder.

6. First, run the `training.py` file. It will train and save the model inside the `all/code` folder.

7. After step 6 is done, run the `prediction.py` file. This file predicts and saves the visualization files inside the `all/data` folder.

## Project Structure

- `all/data/`
  - `images/` (Put your image files here)
  - `roi_folder/` (Put your shape file here)
  - `crop_mask.tif`
- `all/code/` (Put your code files here)
  - `training.py`
  - `prediction.py`
  - `model.py`
  - `datapreprocessing.py`

## Running the Code

1. Navigate to the `all/code` folder.

2. Open a terminal or command prompt.

3. Run the following commands:

   For training the model:
      - python3 training.py

   For prediction:
      - python3 prediction.py
