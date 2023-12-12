import pyotb
import os

datapath = '/home/otbuser/all/data/'
xs_img = os.path.join(datapath , "area2_0123_2023_8bands_norm.tif")

os.environ["OTB_TF_NSOURCES"] = "1"
infer = pyotb.TensorflowModelServe({
    "source1.il": xs_img,
    "source1.rfieldx": 64,
    "source1.rfieldy": 64,
    "source1.placeholder": "input_xs",
    "model.dir": os.path.join(datapath , "output/savedmodel") ,
    "model.fullyconv": True,
    "output.names": "argmax_layer_crop16",
    "output.efieldx": 32,
    "output.efieldy": 32
})
ext_fname = "gdal:co:COMPRESS=DEFLATE"
infer.write(os.path.join(datapath , "output/created_map.tif"), pixel_type="uint8", ext_fname=ext_fname)
