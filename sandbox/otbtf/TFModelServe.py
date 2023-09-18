import otbApplication

print("hello")
# Create the OTBTF application
app = otbApplication.Registry.CreateApplication("TensorflowModelServe")

# Set the input parameters
app.SetParameterString("source1", "/root/cocktail/data/collection/area2_square_0709_2022_sentinel2/T50LKR_20220709T022601_B02.tif")
app.SetParameterInt("source1.rfieldx", 16)
app.SetParameterInt("source1.rfieldy", 16)
app.SetParameterString("source1.placeholder", "x")

app.SetParameterString("model.dir", "/home/otbuser/all/data/")
app.SetParameterString("output.names", "prediction")
app.SetParameterString("out", "classif_model1.tif?&box=4000:4000:1000:1000")

# Execute the application
app.ExecuteAndWriteOutput()
