# utilities module
# Dec 2024, RTS

import math
import time
import numpy
from osgeo import gdal

#------------------------------------------------------------------------------------------
def get_coordinates(latitude,longitude,surface_area):
    R = 6371.0 # Calculate the side length of the square in km
    side_length = math.sqrt(surface_area)
    # Convert side length to degrees (approximation)
    delta_lat = (side_length / R) * (180 / math.pi)
    delta_lon = (side_length / R) * (180 / math.pi) / math.cos(math.radians(latitude))
    top_left = [longitude - delta_lon / 2, latitude + delta_lat / 2]
    bottom_right = [longitude + delta_lon / 2, latitude - delta_lat / 2]
    return (top_left+ bottom_right)
    
#------------------------------------------------------------------------------------------   
def download_relevant_files(assets, filtered_images, selected_coords, folder):
  res = {}
  for i in assets:
    if i.name in filtered_images:
      lat, longt = selected_coords
      lat, longt = abs(int(lat)),abs(int(longt))
      timestamp = int(time.time())
      base_name = i.name.split('.')[0]
      i.name = f"{base_name}_{lat}_{longt}_{timestamp}.tif"
      res[i.name] = i
      i.download(target=folder)
  return (res)

#------------------------------------------------------------------------------------------ 
# visualize a RGB from IR-RGB Sentinel-2 geotif
def process_geotiff(file, bands, datapath ):
    # Open the dataset
    dataset = gdal.Open(datapath + file)

    if dataset is None:
        print(f"Unable to open {file}")
        return None

    # Get dataset information
    num_bands = dataset.RasterCount
    print(f"Number of bands: {num_bands}")

    # Check if the file has at least 3 bands (for RGB)
    if num_bands < 3:
        print("This file doesn't have enough bands for true color display.")
        return None

    # Read the red, green, and blue bands
    # Sentinel-2 bands: 4 (Red), 3 (Green), 2 (Blue)
    arr = []
    for i in bands:
      if i not in range(1,num_bands+1):
        print(f"Invalid band number: {i}")
        return None
      band = dataset.GetRasterBand(i).ReadAsArray().astype(numpy.float32)
      arr.append(band)

    # Stack bands directly
    rgb = numpy.dstack(arr)
    # Normalize the data
    rgb_normalized = (rgb - numpy.min(rgb)) / (numpy.max(rgb) - numpy.min(rgb))

    return(rgb_normalized)
#------------------------------------------------------------------------------------------

def adjust_brightness_contrast_npy(dataset, bands, brightness, contrast):
    """
    Adjust brightness and contrast of the image

    Parameters:
    image: 3-band normalized numpy array generated from .tif (process_tif)
    brightness: Brightness factor (>1 increases brightness, <1 decreases brightness)
    contrast: Contrast factor (>1 increases contrast, <1 decreases contrast)
    """
    # Adjust brightness
    adjusted = dataset * brightness

    # Adjust contrast
    adjusted = (adjusted - 0.5) * contrast + 0.5

    # Clip values to 0-1 range
    adjusted = numpy.clip(adjusted, 0, 1)
    return (adjusted)
#------------------------------------------------------------------------------------------