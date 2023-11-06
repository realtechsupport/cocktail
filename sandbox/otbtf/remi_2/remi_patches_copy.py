import pyotb
import os

labels_img = "/home/otbuser/all/data/crop_mask.tif"
vec_train = "/home/otbuser/all/data/area2_0123_2023_raster_classification_13_points_A.shp"
vec_valid = "/home/otbuser/all/data/area2_0123_2023_raster_classification_13_points_B.shp"

os.environ["OTB_TF_NSOURCES"] = "2"

# xs_image as multiband_image - 8 bands in our case
xs_img =  ("/home/otbuser/all/data/area2_0530_2022_8bands.tif")
## passing p_img as monoband_image
p_img =  ("/home/otbuser/all/data/area2_0530_2022_8bands_flattened.tif")

for num,vec in enumerate([vec_train, vec_valid]):
    new_labels_img = labels_img.replace("crop_mask", f"class_labels_{num+1}")
    app_extract = pyotb.PatchesExtraction({
        "source1.il": p_img,
        "source1.patchsizex": 16,
        "source1.patchsizey": 16,
        "source1.nodata": 0,
        "source2.il": xs_img,
        "source2.patchsizex": 16,
        "source2.patchsizey": 16,
        "source2.nodata": 0,
        "vec": vec,
        "field": "class",
        "outlabels": new_labels_img,
    })
    name = vec.replace("raster_classification_13_points", "").replace(".shp", "")
    out_dict = {
        "source1.out": name + "_p_patches.tif",
        "source2.out": name + "_xs_patches.tif",
    }
    pixel_type = {
        "source1.out": "int16",
        "source2.out": "int16",
    }
    ext_fname = "gdal:co:COMPRESS=DEFLATE"
    app_extract.write(out_dict, pixel_type=pixel_type, ext_fname=ext_fname)