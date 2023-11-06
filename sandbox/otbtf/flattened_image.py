# Helper file with various functions to support OTBTF based GEOAI
# Scale and normalize geotif image
# June 2023
# -------------------------------------------------------------------
import numpy as np
from osgeo import gdal
#---------------------------------------------------------------------

def scale_and_normalize(datapath, input, output, scale_min, scale_max):
    input_dataset = gdal.Open(datapath + input)
    input_data = input_dataset.ReadAsArray()

    original_min = input_data.min()
    original_max = input_data.max()

    # Scaling
    scaled_data = (input_data - original_min) * ((scale_max - scale_min) / (original_max - original_min)) + scale_min
    # scaled_data = input_data
    # normalized_data = input_data
    # Normalize [0, 1]
    normalized_data = (scaled_data - scale_min) / (scale_max - scale_min)

    # Output dataset
    driver = gdal.GetDriverByName("GTiff")
    output_dataset = driver.Create(datapath + output, input_dataset.RasterXSize, input_dataset.RasterYSize, 1, gdal.GDT_Float32)

    print("This is the band", range(input_dataset.RasterCount))
    print("This si the range 1", range(1))
    # Writing normalized data to output dataset

    for band in range(1):
        output_dataset.GetRasterBand(band + 1).WriteArray(normalized_data[band])

    # Set the georeferencing information
    output_dataset.SetGeoTransform(input_dataset.GetGeoTransform())
    output_dataset.SetProjection(input_dataset.GetProjection())

    # Close the datasets
    input_dataset = None
    output_dataset = None

#--------------------------------------------------------------------------------


datapath = "/home/otbuser/all/data/"
print("datapath: ", datapath)

# ------------------------------------------------------------------------------
# Ensure that the input image is normalized before proceeding with the next steps
input = 'area2_0530_2022_8bands.tif'
normalized_input = 'area2_0530_2022_8bands_flattened.tif'
scale_min = 0
scale_max = 65535
# print(input.shape, normalized_input.shape)

scale_and_normalize(datapath, input, normalized_input, scale_min, scale_max)