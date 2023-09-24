#  Example on the use of the Smoothing application

# The python module providing access to OTB applications is otbApplication
import otbApplication as otb

# Let's create the application with codename "Smoothing"
app = otb.Registry.CreateApplication("Smoothing")

# We set its parameters
app.SetParameterString("in", "/home/otbuser/all/data/area2_0530_2022_8bands.tif")
app.SetParameterString("type", "mean")
app.SetParameterString("out", "/home/otbuser/cocktail/sandbox/images/my_output_image.tif")

# This will execute the application and save the output file
app.ExecuteAndWriteOutput()