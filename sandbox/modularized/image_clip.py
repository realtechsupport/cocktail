from osgeo import gdal, osr

def image_clipping(datapath, tiff_file, shape_file):
    rasterfile = gdal.Open(datapath + tiff_file)
    print('\nPerforming the clip operation...\n')
    warp_options = gdal.WarpOptions(cutlineDSName = datapath + shape_file, cropToCutline = True)
    rasterfile_new = tiff_file.split('.tif')[0] + '_roi.tif'
    ds = gdal.Warp(datapath + rasterfile_new, datapath + tiff_file,  options = warp_options)

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




image_clipping("/home/otbuser/all/data/", "area2_0530_2022_8bands.tif", "area2_0123_2023_raster_classification_13_points_A.shp")