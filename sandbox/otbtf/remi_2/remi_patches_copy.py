import pyotb
import os

datapath = '/home/otbuser/all/data/'


xs_img = os.path.join(datapath , "area2_0123_2023_8bands_norm.tif")
labels_img =  os.path.join(datapath, "area2_0123_2023_8bands_norm_labelimage.tif")

vec_train = os.path.join(datapath, "area2_0123_2023_training_centroids.gpkg")
vec_test = os.path.join(datapath, "area2_0123_2023_testing_centroids.gpkg")


pyotb.PatchesSelection({
    "in": labels_img,
    "grid.step": 10,
    "grid.psize": 10,
    "strategy": "split",
    "strategy.split.trainprop": 0.80,
    "strategy.split.testprop": 0.20,
    "outtrain": vec_train,
    "outtest": vec_test
})

os.environ["OTB_TF_NSOURCES"] = "2"

for num,vec in enumerate([vec_train, vec_test]):
    # new_labels_img = labels_img.replace("crop_mask", f"class_labels_{num+1}")
    app_extract = pyotb.PatchesExtraction({
        "source1.il": xs_img,
        "source1.patchsizex": 8,
        "source1.patchsizey": 8,
        "source2.il": labels_img,
        "source2.patchsizex": 8,
        "source2.patchsizey": 8,
        "vec": vec,
        "field": "id",
        # "outlabels": new_labels_img,
    })
    name = vec.replace("_centroids", "").replace(".gpkg", "")
    out_dict = {
        "source1.out": name + "_xs_patches.tif",
        "source2.out": name + "_labels_patches.tif",
    }
    pixel_type = {
        "source1.out": "float",
        "source2.out": "uint8",
    }
    ext_fname = "gdal:co:COMPRESS=DEFLATE"
    app_extract.write(out_dict, pixel_type=pixel_type, ext_fname=ext_fname)