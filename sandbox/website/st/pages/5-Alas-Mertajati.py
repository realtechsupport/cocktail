# GISlogics - Alas Mertajati
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

imagepath = "/home/otbuser/all/data/images/"
videopath = "/home/otbuser/all/data/videos/"
#---------------------------------------------------------
st.set_page_config(
    page_title="GeoAiLogics",
    page_icon=" RTS ",
    layout="wide"
)
#--------------------------------------------------------
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
#---------------------------------------------------------
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

#----------------------------------------------------------
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

stitle =  '<p style="text-align: center; font-size: 18px;">Alas Mertajati</p>'
st.markdown(stitle, unsafe_allow_html=True)
st.markdown("")
st.markdown("")


text = ("The Mertajati Forest, the Alas Mertajati, is located in the highlands of Central Bali adjacent"
" to Lake Tamblingan. The area is home to Casuarina and ancient Banyan trees and serves as a vital source of fresh water."
" The water from Mertajati holds a privileged position amongst the Indigenous People of _Dalem Tamblingan Catur Desa_,"
" who have inhabited the region for centuries. Mertajati is revered as a life source and is honored in various"
" ceremonies held throughout the year.")
st.markdown(text)

image = "mertajati_72dpi.jpg"
d = Image.open(imagepath + image)
st.image(d, width="50%", use_column_width=True)
st.caption("Alas Mertajati and the Buleleng and Tabanan Regencies in the highlands of Central Bali. GIS data"
"  provided by the WISNU foundation. Image source: Superdove, Planet Labs, May 30, 2022")

text = ("The subak irrigation system, first documented in the 9th century, is an egalitarian water management"
" concept employed by local farmers to manage limited water resources. It involves a network of canals"
" and terraces carved into the hillsides, allowing for the careful and equitable distribution of water during the"
" dry season. The subak system has been at the core of sustainable resource control long before the term became"
" fashionable. The subak method integrates the Balinese _Tri Hita Karana_ philosophy, the three sources of well-being,"
" into multi-generational land stewardship practices, setting Balinese terrace management apart from similar practices in East Asia."
" In recognition of its cultural and environmental value, the subak water management system was declared a"
" UNESCO World Heritage Site in 2012, making it not only a source of pride for the Balinese but a premier"
" tourist attraction.")
st.markdown(text)

video = "ForestLakeTamblingan_silent.mp4"
video_file = open(videopath + video, 'rb')
video_bytes = video_file.read()
st.video(video_bytes)
st.caption("Alas Mertajati. Protected forest adjacent to lake Tamblingan. Video by RTS.")


text = ("The Alas Mertajati is a significant resource both as forested lands and as a water catchment system."
" Tropical rains fill the groundwater and streams that flow from the forests in the mountain areas to lower"
" elevations into agriculture plots. Situated in the highlands, the Alas Mertajati spans the"
" hillsides of ancient volcanoes, ranging in elevation from 300 to 2000 meters above sea level. Due to this"
" elevation, the temperatures in the Mertajati highlands are notably lower, creating a unique microclimate"
" that supports year-round harvests of a diverse collection of fruits, plants, flowers, and vegetables."
" The local soils, known as andosols, are dark, mineral-rich, and highly porous as a result of their volcanic"
" origin. Coupled with a consistent supply of leaf litter from the perpetually lush vegetation, these nutrient-rich"
" soils provide excellent conditions for plant cultivation and food production. The Alas Mertajati is a special place.")
st.markdown(text)

#----------------------------------------------------------------------------------------------------------------

