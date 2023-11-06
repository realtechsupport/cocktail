# GISlogics - Seeing like a satellite
import os, sys
import time
import numpy as np

import tensorflow as tf

import otbtf
import otbApplication

import otbtf.tfrecords
import otbtf.utils

from osgeo import gdal
from otbtf import DatasetFromPatchesImages
from otbtf.model import ModelBase
from otbtf import TFRecords
from otbtf.examples.tensorflow_v2x.fcnn import fcnn_model
from otbtf.examples.tensorflow_v2x.fcnn import helper
from PIL import Image
from tricks import *

from osgeo import gdal

import streamlit as st

sys.path.append("/home/otbuser/all/code/")
from streamlit_helper import *

datapath =  "/home/otbuser/all/data/"
imagepath = "/home/otbuser/all/data/images/"
videopath = "/home/otbuser/all/data/videos/"
modelpath =  "/home/otbuser/all/data/models/"
#---------------------------------------------------------
st.set_page_config(
    page_title="GeoAiLogics",
    page_icon=" RTS ",
    layout="wide"
)
#---------------------------------------------------------
streamlit_style = """
                <style>
                @import url("https://fonts.googleapis.com/css2?family=Hina+Mincho:wght@100&display=swap");
                html, body, [class*="css"]  {
                font-family: 'Hina Mincho', serif;
                font-size: 16px;
                }
                </style>
                """
st.markdown(streamlit_style, unsafe_allow_html=True)

#----------------------------------------------------------
hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

#---------------------------------------------------------
# Remove space on top
st.markdown("""
        <style>
        .appview-container .main .block-container {{
        padding-top: {padding_top}rem;
        padding-bottom: {padding_bottom}rem;}}
        </style>""".format(padding_top=1, padding_bottom=1),unsafe_allow_html=True,)
#----------------------------------------------------------  
#st.sidebar.caption("TABLE of CONTENTS\n\n")
#st.sidebar.write("0.  Introduction\n\n1.  From Orbit to Earth\n\n2.  Open Lands\n\n3.  Planetary Positions\n\n4.  Banana Coffee Taro\n\n5.  Learning from Tuvalu\n\n6.  Conclusion")

# --------------------------------------------------------

stitle =  '<p style="text-align: center; font-size: 18px;">Seeing like a satellite</p>'
st.markdown(stitle, unsafe_allow_html=True)
st.markdown("")
st.markdown("")


text = ("Satellite images are a distinct category of digital images. They incorporate additional descriptors beyond what is found in photographs."
" Satellite images contain spectral information imperceptible to human vision together with geocoding information. As such, they constitute a"
" particularly densely packed form of image representation and expand the category of _operational images_, to use the term coined by Harun Farocki.")
st.markdown(text)


text = ("Satellite images can be categorized along three dimensions. First, spatial resolution, or the number of pixels per meter."
" Second, the temporal resolution,  the time gap between scans of a given area. Third, spectral resolution, which represents the"
" dynamic range of the electromagnetic frequency spectrum that the satellite sensors can capture. These frequency bands typically"
" encompass the colors visible to human beings and often include many more windows onto the light reflected from the Earth’s surface."
" Satellite imagery is typically encoded in a dedicated format, _GeoTIF_, that expands the existing TIF image file structure with geolocation"
" metatags, and ensures compatibility across platforms.")
st.markdown(text)


text = ("Land cover classification relies on analyzing the spectral reflectance of sunlight"
" from the ground as captured from orbit. Different kinds of land cover, ranging from arid desert to humid rainforests,"
" exhibit varying levels of reflectance. These varied reflectance patterns can be considered as signatures, unique features"
" associated with the sources of the reflected energy."
" Image processing algorithms collect and analyze these signatures as information for land cover classification." 
" When the reflectance signatures are geolocated in the field, they serve as grounding operators, enabling an algorithm"
" to associate an actual location on the Earth's surface with its corresponding spectral representation in a satellite image."
" The combination of spatial, spectral and temporal information produces a unique place-based mathematical representation of a particular"
" area of the Earth’s surface. The patterns contained within these representations are a satellite’s view of the landscape.")
st.markdown(text)

image = "Mertajati+Sumatra_hires.jpg"
d = Image.open(imagepath + image)
st.image(d, width="50%", use_column_width=True)
st.caption("Right: Palm oil plantation, Sumatra, Indonesia. Source: Planet Labs, May 20, 2015."
" Left: Mixed forest and agroforestry plots in the highlands of the Alas Mertajati. Source: Planet Labs, June 17, 2017."
" Both images contain 4 spectral bands (red, blue, green, and near-infrared. Both images have a spatial resolution of 3.7 meters/pixel.")

text = ("The patterns can capture signatures of human intervention in the landscape."
" Above are two images depicting tropical farmlands. Both images are obtained from the Dove satellite"
" constellation of Planet Labs. The first image showcases a palm farm in Sumatra, characterized by"
" a large-scale monoculture system designed for efficient palm oil production. In contrast, the"
" farmlands in the highlands of Bali exhibit a haphazard arrangement. The presence of small-scale"
" farming practices and complex land ownership conditions is reflected in the patchwork of greenery"
" across the landscape. Due to the emphasis on small plot cultivation in a hilly terrain, irregularly"
" shaped land plots are the norm. In a climate where plant growth occurs continuously, with plants"
" flowering on a weekly basis, change is a constant factor. The machinery of GeoAI, utilizing pixels"
" and algorithms designed to detect patterns and regularities, seems to be more at home in the"
" rectangular parcels of plantations.")
st.markdown(text)

image = "SpatialResolution.jpg"
d = Image.open(imagepath + image)
st.image(d, width="50%", use_column_width=True)
st.caption("Spatial resolution of satellite assets. False color and true color rendering of the agroforestry site captured by"
" Dove, Superdove and Sentinel-2 satellites, showing differences in spatial resolution. Focus area (yellow) is an agroforestry site")

text = ("The expressive power of an orbital asset is given by the combination of the three features temporal, spatial and spectral resolution,"
" and each satellite system has its own combination of these features that make it useful for some tasks, while not for others."
" The European Space Agency’s Sentinel-2 satellites have 14 distinct bands, whereas Planet Labs SuperDove"
" constellation only has 8. However, SuperDove has a temporal resolution of 1 day whereas Sentinel-2 has one of 5 days."
" While SuperDove has a spatial resolution of 3.7 meters/pixel, Sentinel-2’s bands produce imagery with resolution ranging from"
" 10 meters to 60 meters. The satellite images above demonstrate how important spatial resolution is for small-scale landscape features."
" Only satellite assets that deliver sufficient spatial and spectral resolution are suitable for observing small-scale agroforestry plots.")
st.markdown(text)

image = "Spectral_D_SD_S.jpg"
d = Image.open(imagepath + image)
st.image(d, width="50%", use_column_width=True)
st.caption("Spectral resolution of satellite assets. Y-axis shows spectral reflectance [in percent] of individual bands from Dove (bands 1-4),"
"  SuperDove (bands: 2,3,6, 8) and Sentinel-2 satellites (bands 1-4) on an agroforestry plot with coffee arabica as the dominant species."
"  SuperDove's band 8 is particularly effective at detecting the signature of coffee arabica, for example.")
