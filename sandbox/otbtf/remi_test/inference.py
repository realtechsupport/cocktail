import pyotb
import os

p_img =  ("/home/otbuser/all/data/spot/PROD_SPOT7_001/VOL_SPOT7_001_A/IMG_SPOT7_P_001_A/"
          "DIM_SPOT7_P_201409171025192_ORT_1190912101.XML")
xs_img = ("/home/otbuser/all/data/spot/PROD_SPOT7_001/VOL_SPOT7_001_A/IMG_SPOT7_MS_001_A/"
          "DIM_SPOT7_MS_201409171025192_ORT_1190912101.XML")

os.environ["OTB_TF_NSOURCES"] = "2"
infer = pyotb.TensorflowModelServe({
    "source1.il": p_img,
    "source1.rfieldx": 64,
    "source1.rfieldy": 64,
    "source1.placeholder": "input_p",
    "source2.il": xs_img,
    "source2.rfieldx": 16,
    "source2.rfieldy": 16,
    "source2.placeholder": "input_xs",
    "model.dir": "/home/otbuser/all/data/output/savedmodel",
    "model.fullyconv": True,
    "output.names": "argmax_layer_crop16",
    "output.efieldx": 32,
    "output.efieldy": 32
})
ext_fname = "gdal:co:COMPRESS=DEFLATE"
infer.write("/home/otbuser/all/data/output/amsterdam_map.tif", pixel_type="uint8", ext_fname=ext_fname)

# python training.py --model_dir /home/otbuser/all/data/output/savedmodel