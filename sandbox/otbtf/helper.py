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

    # Normalize [0, 1]
    normalized_data = (scaled_data - scale_min) / (scale_max - scale_min)

    # Output dataset
    driver = gdal.GetDriverByName("GTiff")
    output_dataset = driver.Create(datapath + output, input_dataset.RasterXSize, input_dataset.RasterYSize, input_dataset.RasterCount, gdal.GDT_Float32)

    # Writing normalized data to output dataset
    for band in range(input_dataset.RasterCount):
        output_dataset.GetRasterBand(band + 1).WriteArray(normalized_data[band])

    # Set the georeferencing information
    output_dataset.SetGeoTransform(input_dataset.GetGeoTransform())
    output_dataset.SetProjection(input_dataset.GetProjection())

    # Close the datasets
    input_dataset = None
    output_dataset = None

#--------------------------------------------------------------------------------


#---------------------------------------------------------------------

def scale_and_normalize_and_flatten(datapath, input, output, scale_min, scale_max):
    input_dataset = gdal.Open(datapath + input)
    input_data = input_dataset.ReadAsArray()

    original_min = input_data.min()
    original_max = input_data.max()

    # Scaling
    scaled_data = (input_data - original_min) * ((scale_max - scale_min) / (original_max - original_min)) + scale_min
    # Normalize [0, 1]
    normalized_data = (scaled_data - scale_min) / (scale_max - scale_min)

    # Output dataset
    driver = gdal.GetDriverByName("GTiff")
    output_dataset = driver.Create(datapath + output, input_dataset.RasterXSize, input_dataset.RasterYSize, 1, gdal.GDT_Float32)

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