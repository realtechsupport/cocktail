# In this file we have functions for image clipping, preprocessing and sampling 
import os
import numpy as np
import rasterio
from osgeo import gdal, osr
import keras
import tensorflow as tf
from keras.utils import to_categorical

# Hardcode value
patch_size = 256

def clipping(datapath, ps, roipath, roishape):
    rasterfile = gdal.Open(datapath + ps)

    print('\nPerforming the clip operation...\n')


    warp_options = gdal.WarpOptions(cutlineDSName = roipath + roishape, cropToCutline = True)
    rasterfile_new = ps.split('.tif')[0] + '_roi.tif'
    print(roipath + rasterfile_new, datapath + ps )
    ds = gdal.Warp(roipath + rasterfile_new, datapath + ps,  options = warp_options)
    print(ds)

    cols = ds.RasterXSize
    rows = ds.RasterYSize
    bands = ds.RasterCount
    projInfo = ds.GetProjection()
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromWkt(projInfo)
    spatialRefProj = spatialRef.ExportToProj4()
    ds = None

    print('\nClipped raster input: ', rasterfile_new)
    print('Checking spatial reference info\n')
    print ("WKT format: " + str(spatialRef))
    print ("Proj4 format: " + str(spatialRefProj))
    print ("Number of columns: " + str(cols))
    print ("Number of rows: " + str(rows))
    print ("Number of bands: " + str(bands))


#target preprocessing

def target_preprocessing(folder_path, patch_size):

    with rasterio.open(folder_path) as src:
        # Read the TIFF data
        output_mask = src.read()

        # Get the shape of the TIFF data
        num_bands, height, width = output_mask.shape

        # Calculate the new width and height that are multiples of the patch size
        new_width = int(np.floor(width / patch_size)) * patch_size
        new_height = int(np.floor(height / patch_size)) * patch_size

        print("cropped dimensions:", new_height, new_width)

        output_mask = np.moveaxis(output_mask, 0, -1)

        # Crop the input_image to the new dimensions
        cropped_mask = output_mask[:new_height, :new_width, :]

    new_mask = np.squeeze(cropped_mask)

    masks = []
    for i in range(0, new_mask.shape[0], patch_size):
        for j in range(0, new_mask.shape[1], patch_size):
            patch = new_mask[i:i+patch_size, j:j+patch_size]
            masks.append(patch)

    mask_array = np.array(masks)

    useful_masks = []
    useless = 0
    indexes = []
    for index,img in enumerate(mask_array):

        val, counts = np.unique(img, return_counts=True)

        if (1 - (counts[0]/counts.sum())) > 0.05:
          useful_masks.append(img)
          indexes.append(index)
        else:
          #print("I am useless")
          useless +=1


    print("Total useful images are: ", len(mask_array)-useless)
    print(indexes)
    print("Total useless images are: ", useless)

    useful_masks_array = np.array(useful_masks)

    useful_masks_onehot = to_categorical(useful_masks_array)


    return useful_masks, useful_masks_onehot, indexes, new_mask

def newclipping(datapath,roipath,ps, roishape):
  rasterfile = gdal.Open(datapath + ps)

  print('\nPerforming the clip operation...\n')


  warp_options = gdal.WarpOptions(cutlineDSName = roipath + roishape, cropToCutline = True)
  rasterfile_new = ps.split('.tif')[0] + '_roi.tif'
  print(roipath + rasterfile_new, datapath + ps )
  ds = gdal.Warp(roipath + rasterfile_new, datapath + ps,  options = warp_options)

  cols = ds.RasterXSize
  rows = ds.RasterYSize
  bands = ds.RasterCount
  projInfo = ds.GetProjection()
  spatialRef = osr.SpatialReference()
  spatialRef.ImportFromWkt(projInfo)
  spatialRefProj = spatialRef.ExportToProj4()
  ds = None

  print('\nClipped raster input: ', rasterfile_new)
  print('Checking spatial reference info\n')
  print ("WKT format: " + str(spatialRef))
  print ("Proj4 format: " + str(spatialRefProj))
  print ("Number of columns: " + str(cols))
  print ("Number of rows: " + str(rows))
  print ("Number of bands: " + str(bands))

  return roipath + rasterfile_new

def preprocessing(filelocation,patch_size, target = None):
    # Load the GeoTIFF file
    with rasterio.open(filelocation) as src:
        # Read the TIFF data
        tiff_data = src.read()
        print("total number of nan in original",np.count_nonzero(np.isnan(tiff_data)))

        # Get the shape of the TIFF data
        num_bands, height, width = tiff_data.shape

        if target: 
            target_array = target[3]
            if height < target_array.shape[0] or width < target_array.shape[1]:
               return False

        print("Original image dimensions:", num_bands, height, width)
        unique_elements, counts_elements = np.unique(tiff_data, return_counts=True)
        print(unique_elements, counts_elements )
        print("total unique",len(counts_elements))

        print(np.min(tiff_data), np.max(tiff_data))


        normalized_image = np.zeros_like(tiff_data, dtype='float32')

        for band, count in enumerate(range(tiff_data.shape[0])):
            band_data = tiff_data[band, :, :]
            band_min = np.min(band_data)
            band_max = np.max(band_data)
            print("band-", count+1,"maximum-",band_max,"minimum-",band_min)
            #print(band_data)
            #epsilon is added to prevent division by zero
            normalized_band = (band_data - band_min) / (band_max - band_min + 1e-10)
            normalized_image[band, :, :] = normalized_band

        # Calculate the new width and height that are multiples of the patch size
        if target: 
            new_height = target_array.shape[0]
            new_width = target_array.shape[1]
        else:
            new_width = int(np.floor(width / patch_size)) * patch_size
            new_height = int(np.floor(height / patch_size)) * patch_size

        print("cropped dimensions:", new_height, new_width)

        input_image = np.moveaxis(normalized_image, 0, -1)

        # Crop the input_image to the new dimensions
        cropped_array = input_image[:new_height, :new_width, :]

    print("total number of nan",np.count_nonzero(np.isnan(cropped_array)))
    print("Cropped array shape:", cropped_array.shape)
    print(np.min(cropped_array), np.max(cropped_array))

    patches = []
    for i in range(0, cropped_array.shape[0], patch_size):
        for j in range(0, cropped_array.shape[1], patch_size):
            patch = cropped_array[i:i+patch_size, j:j+patch_size]
            patches.append(patch)
    print("patches are created")
    return patches, cropped_array

def sampling(patches,indexes):
    useful_patches = []
    for number_of_masks,i in enumerate(indexes):
      print(i)
      if i < len(patches):
        useful_patches.append(patches[i])
      else:
        break
    return useful_patches, number_of_masks


def process_images_in_folder(datapath, patch_size, roipath,target, roishape = 'area2_square.geojson'):
    # Initialize an empty list to store the sampled patches and target_patches
    sampled_image_patches = []
    target_patches = []

    # Loop through all files in the folder
    for ps in os.listdir(datapath):

        # #print(type(filename),filename.split('.tif')[0] + '_roi.tif' )
        # print(folder_path + ps)
        # print(roipath + roishape)
        # print(ps)

        # Apply clipping
        clipped_image_path = newclipping(datapath,roipath,ps, roishape)

        # Preprocess(normalize,resize,create patches) the clipped image
        if preprocessing(clipped_image_path, patch_size): 
            patches, CA = preprocessing(clipped_image_path, patch_size)
            print(len(patches))
        else: 
            continue 

        # Sample patches from the processed image patches and create corresponding target patches
        #print(target[2])
        #print(len(target[2]))
        useful_patches, number_of_masks = sampling(patches,target[2])
        sampled_image_patches.extend(useful_patches)
        target_patches.extend(target[1][0:number_of_masks])
        print(len(sampled_image_patches),len(target_patches) )


    return sampled_image_patches,target_patches

