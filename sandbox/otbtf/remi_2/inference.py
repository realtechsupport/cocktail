import pyotb
import os


xs_img = ("/home/otbuser/all/data/patches_selection/new/area2_0530_2022_8bands.tif")

os.environ["OTB_TF_NSOURCES"] = "1"
infer = pyotb.TensorflowModelServe({
    "source1.il": xs_img,
    "source1.rfieldx": 64,
    "source1.rfieldy": 64,
    "source1.placeholder": "input_xs",
    "model.dir": "/home/otbuser/all/data/patches_selection/output_test/savedmodel",
    "model.fullyconv": True,
    "output.names": "argmax_layer_crop16",
    "output.efieldx": 32,
    "output.efieldy": 32
})
ext_fname = "gdal:co:COMPRESS=DEFLATE"
infer.write("/home/otbuser/all/data/patches_selection/new/output/created_map.tif", pixel_type="uint8", ext_fname=ext_fname)
