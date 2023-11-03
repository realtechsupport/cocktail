import pyotb

labels_img = "/home/otbuser/all/data/remi_copy.tif"
vec_train = "/home/otbuser/all/data/area2_0123_2023_raster_classification_13_points_A.shp"

# vec_train = "/home/otbuser/all/data/area2_0123_2023_raster_classification_13_vecstats.xml"
# vec_valid = "/home/otbuser/all/data/output/vec_valid.geojson`"
vec_valid = "/home/otbuser/all/data/area2_0123_2023_raster_classification_13_points_B.shp"

import os
os.environ["OTB_TF_NSOURCES"] = "1"

p_img =  ("/home/otbuser/all/data/area2_0530_2022_8bands.tif")
# xs_img = ("/home/otbuser/all/data/spot/PROD_SPOT7_001/VOL_SPOT7_001_A/IMG_SPOT7_MS_001_A/"
#           "DIM_SPOT7_MS_201409171025192_ORT_1190912101.XML")
out_pth = "/home/otbuser/all/data/test_output/"

for vec in [vec_train, vec_valid]:
    app_extract = pyotb.PatchesExtraction({
        "source1.il": p_img,
        "source1.patchsizex": 64,
        "source1.patchsizey": 64,
        "source1.nodata": 0,
        # "source2.il": xs_img,
        # "source2.patchsizex": 16,
        # "source2.patchsizey": 16,
        # "source2.nodata": 0,
        
        # "source2.patchsizex": 64,
        # "source2.patchsizey": 64,
        "vec": vec,
        "field": "class",
        "outlabels": labels_img,
    })
    name = vec.replace("raster_classification_13_points", "").replace(".shp", "")
    out_dict = {
        "source1.out": name + "_p_patches.tif",
        # "source2.out": name + "_labels_patches.tif",
        # "source3.out": name + "_labels_patches.tif",
    }
    pixel_type = {
        "source1.out": "int16",
        # "source2.out": "int16",
        # "source3.out": "uint8",
    }
    ext_fname = "gdal:co:COMPRESS=DEFLATE"
    app_extract.write(out_dict, pixel_type=pixel_type, ext_fname=ext_fname)


