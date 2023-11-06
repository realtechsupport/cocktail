# GISlogics - agroforestry
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
# --------------------------------------------------------

stitle =  '<p style="text-align: center; font-size: 18px;">Agroforestry in the Alas Mertajati</p>'
st.markdown(stitle, unsafe_allow_html=True)
st.markdown("")
st.markdown("")


text = ("Agroforestry refers to land use systems that combine woody perennials such as trees, shrubs, palms, and bamboos"
" with agricultural crops and animals in unique temporal and special arrangements. These systems typically exhibit a"
" higher species diversity compared to other agroecosystems , and their spatial structure undergoes significant changes"
" over time. Unlike monoculture farming, agroforestry systems do not rely on a single crop, allowing farmers to adapt their"
" plant selection to variations in water and soil conditions within a particular plot. The diverse root systems of multiple"
" plants and trees in agroforestry plots facilitate higher water absorption rates, reducing runoff and serving as effective"
" erosion barriers.")
st.markdown(text)

text = ("Imagine agroforestry plots as three-dimensional semi-wild gardens. The horizontal dimension features"
" plants distributed in irregular patterns, and the vertical dimension is dominated by trees. Within these plots,"
" a combination of mature and maturing trees coexist with shrubs, vegetables, spice crops, and shade-tolerant grasses."
" Although an agroforestry plot may appear unorganized, it is intentionally designed to sustain high productivity across"
" a diverse range of plants, even under adverse environmental conditions. Well-maintained agroforestry plots serve as"
" robust, sustainable, and efficient uses of arable land. Agroforestry is a case study in fault-tolerant farming.")
st.markdown(text)
video = "Agroforestry_20221229_024910182_silent.mp4"
video_file = open(videopath + video, 'rb')
video_bytes = video_file.read()
st.video(video_bytes)
st.caption("Agroforestry site in the Tamblingan lands surrounding the Alas Mertajati (-8° 16' 0.659'' S, 115° 4' 31.773'' E). Video by RTS.")

text = (" One of the key advantages of agroforestry is its adaptability"
" to varying rainfall patterns, making it less susceptible to climatic fluctuations. This enhances the resilience of"
" rural farmers and contributes to improved food security. Additionally, agroforestry systems are typically small-scale"
" operations managed by a limited number of farmers who have strong family and personal connections to the land."
" The selection of plant species in agroforestry is often guided by local ecological knowledge that has been passed down"
" through generations. A well-chosen configuration of plant species in agroforestry sites also reduces the need for fertilizers"
" and pesticides. Manure from small-scale animal husbandry is commonly utilized as a natural fertilizer, particularly"
" for clove trees.")
st.markdown(text)

video = "Agroforestry_20221229_022953716_silent.mp4"
video_file = open(videopath + video, 'rb')
video_bytes = video_file.read()
st.video(video_bytes)
st.caption("Agroforestry site in the Tamblingan lands surrounding the Alas Mertajati (-8° 16' 5.487'' S, 115° 5' 50.410'' E). Video by RTS.")

text = ("In Bali, different agroforestry configurations have been developed to suit various food production needs and spatial constraints."
" These configurations include the _abian_, a field located at some distance to a residential area. The _kebon_, a garden located"
" close to a residence and the _telajakan_, a green space directly adjacent to a residence. Accessibility is of prime importance,"
" specifically along the steep slopes of the hills and valleys surrounding the volcanic landscape. For that reason, plots are"
" typically located adjacent to pathways or small streets, facilitating the transport of produce from the fields to market.")
st.markdown(text)

video = "Agroforestry_20221229_030003082_silent.mp4"
video_file = open(videopath + video, 'rb')
video_bytes = video_file.read()
st.video(video_bytes)
st.caption("Agroforestry site in the Tamblingan lands surrounding the Alas Mertajati (-8° 16' 2.767'' S, 115° 4' 43.765'' E). Video by RTS.")

text = ("Agroforestry is currently not recognized as an official land cover category by the Indonesian Geospatial Information Agency (BIG)."  
" Including established and well-maintained agroforestry plots in a land cover classification map in Indonesia is tantamount"
" to the recognition of alternate, sustainable agriculture and land care practices. However, such an acknowledgment raises significant"
" questions regarding land ownership, a process that the land ownership elite might prefer to avoid. Agroforestry is not performed by large"
" corporations. Tending to agroforestry plots is a labor-intensive process, and that labor is performed largely by hand, by the hands"
" of land-less workers. At the same time, agroforestry is more than a food production method. Agroforestry is a way of life that engages with the land"
" on principles that can defy the logics of monetary gain maximization. For the Indigenous People of Dalem Tamblingan, agroforestry represents one aspect of"
" their connection with the landscape and serves as documentation of spiritually grounded, sustainable land use practices. By incorporating agroforestry"
" plots into a land map, these sustainability practices are given cartographic authority, and increased credibility vis-à-vis government agencies.")

st.markdown(text)

image = "agroforestry_typology.jpg"
d = Image.open(imagepath + image)
st.image(d, width="50%", use_column_width=True)
st.caption("Agroforestry plot typology in the Tamblingan lands surrounding the Alas Mertajati. There is significant variation in the types of plants in agroforestry plots as"
" well as in the intensity of intervention into the landscape. Field data collected in January 2023."
" Left: Low-level intervention on a semi-wild site on a steep hill with sugarplum, banana, coffee, taro, clove, and jackfruit."
" Middle: Mid-level intervention with coffee, banana, mandarin, and avocado."
" Right: Mid to high-level intervention with coffee, banana, flowers, and clove.")

#----------------------------------------------------------

