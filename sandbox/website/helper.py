# Helper file with various functions to support OTBTF based GEOAI
# Scale and normalize geotif image
# June 2023
# -------------------------------------------------------------------
import numpy 
from osgeo import gdal
from PIL import Image
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
def ndvi_superdove(imagepath, datapath, input, output):
	# red: band 6, ir band 8
	# https://developers.planet.com/docs/apis/data/sensors/
	numpy.seterr(divide='ignore', invalid='ignore')

	# create ndvi tif image

	tmp = "tmp_ndvi.tif"
	data = gdal.Open(imagepath + input)
	red = data.GetRasterBand(6).ReadAsArray().astype(numpy.float32)
	nir = data.GetRasterBand(8).ReadAsArray().astype(numpy.float32)
	
	#ndvi =  numpy.divide((red - nir), (red + nir))
	ndvi = numpy.divide((nir - red), (nir + red))
	drv = gdal.GetDriverByName ( "GTiff" )
	dst_ds = drv.Create(datapath + tmp, data.RasterXSize, data.RasterYSize, 1, gdal.GDT_Float32, options=["COMPRESS=LZW"])
	dst_ds.SetGeoTransform(data.GetGeoTransform())
	dst_ds.SetProjection(data.GetProjection())
	dst_ds.GetRasterBand(1).WriteArray(ndvi)
	dst_ds.FlushCache()
	dst_ds = None

	#check
	#timg = gdal.Open(datapath + tmp)
	#timg_stats = timg.GetRasterBand(1).GetStatistics(0,1)
	#min_val = timg_stats[0]
	#max_val = timg_stats[1]
	#print("min, max of nvdi tif: ", min_val, max_val)

	# convert to 8 bit .png
	scale = '-scale -1 1 0 255'
	options_list = ['-ot Byte', '-of PNG', scale]
	options_string = " ".join(options_list)
	ds = gdal.Translate(datapath + output, datapath + tmp, options=options_string)
	ds = None
#---------------------------------------------------------------------------------
