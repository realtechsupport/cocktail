import pyotb
import os

xs_img = ("/home/otbuser/all/data/training/area2_0123_2023_8bands_norm.tif")
labels_img =  "/home/otbuser/all/data/patches_selection/new/new_terrain_truth_rasterized.tif"

vec_train = "/home/otbuser/all/data/patches_selection/new/output/vec_train_new.geojson"
vec_valid = "/home/otbuser/all/data/patches_selection/new/output/vec_valid_new.geojson"
vec_test = "/home/otbuser/all/data/patches_selection/new/output/vec_test_new.geojson"


pyotb.PatchesSelection({
    "in": labels_img,
    "grid.step": 8,
    "grid.psize": 8,
    "strategy": "split",
    "strategy.split.trainprop": 0.80,
    "strategy.split.validprop": 0.10,
    "strategy.split.testprop": 0.10,
    "outtrain": vec_train,
    "outvalid": vec_valid,
    "outtest": vec_test
})

os.environ["OTB_TF_NSOURCES"] = "2"

for num,vec in enumerate([vec_train, vec_valid, vec_test]):
    # new_labels_img = labels_img.replace("crop_mask", f"class_labels_{num+1}")
    app_extract = pyotb.PatchesExtraction({
        "source1.il": xs_img,
        "source1.patchsizex": 32,
        "source1.patchsizey": 32,
        "source1.nodata": 0,
        "source2.il": labels_img,
        "source2.patchsizex": 32,
        "source2.patchsizey": 32,
        "source2.nodata": 0,
        "vec": vec,
        "field": "id",
        # "outlabels": new_labels_img,
    })
    name = vec.replace("_new", "").replace(".geojson", "")
    out_dict = {
        "source1.out": name + "_xs_patches_label_new.tif",
        "source2.out": name + "_labels_patches.tif",
    }
    pixel_type = {
        "source1.out": "float",
        "source2.out": "uint8",
    }
    ext_fname = "gdal:co:COMPRESS=DEFLATE"
    app_extract.write(out_dict, pixel_type=pixel_type, ext_fname=ext_fname)