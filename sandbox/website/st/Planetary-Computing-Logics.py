# GISlogics - main
# streamlit will use whichever display mode you have active on mobile
# light or dark based on mobile settings (battery saver)
#--------------------------------------------------------------------
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
modelpath =  "/home/otbuser/all/data/models/"
#---------------------------------------------------------
st.set_page_config(
    page_title="GeoAiLogics",
    page_icon=" RTS ",
    layout="wide"
)
#---------------------------------------------------------
# Select a custom font
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
# ---------------------------------------------------------
# Remove space on top
st.markdown("""
	<style>
	.appview-container .main .block-container {{
	padding-top: {padding_top}rem;
	padding-bottom: {padding_bottom}rem;}}
	</style>""".format(padding_top=1, padding_bottom=1),unsafe_allow_html=True,)
#----------------------------------------------------------
# Hide annoying features
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

title =  '<p style="text-align: center; font-size: 36px;">On the Logics of Planetary Computing</p>'
st.markdown(title, unsafe_allow_html=True)
stitle =  '<p style="text-align: center; font-size: 18px;"><i>With a case study of GeoAI in the Alas Mertajati of Central Bali, Indonesia</i></p>'
st.markdown(stitle, unsafe_allow_html=True)

st.markdown("")
st.markdown("")

image = "NASA-Apollo8-Dec24-1968-Earthrise.jpg"
d = Image.open(imagepath + image)
st.image(d, width="50%", use_column_width=True)
st.caption("Earthrise (public domain), taken on December 24, 1968, by Apollo 8 astronaut William Anders.")


text = ("The iconic photograph of planet earth taken by astronauts in lunar orbit on December 24th 1968 showed our planet as a blue marble, suspended in the vastness of space."
" The image instilled in many people a sense of awe and amazement. Today, however, imagery collected from low-earth orbiting satellites are more likely to instill fear of surveillance,"
" urges for compliance and suggest opportunities for prediction.")
st.markdown(text)

text = ("Within the span of 15 years, the field of satellite-based remote sensing has morphed from nation-state-scale operations focused on research and defense to venture capital financed"
" startups focused on commercial opportunities. Hundreds of satellites have been placed into low-earth orbit, with thousands more slated to join the party." )
st.markdown(text)

text = ("This project places these new low-orbit earth observation assets into the larger context of planet scale computing operating beyond the confines of nation state boundaries."
" The project considers the significance of the combination of low-orbit earth observation systems imaging the surface of the earth and the large scale computational operations that"
" support them. The integration of remote sensing, geography and AI, _GeoAI_, is the lynchpin with which I consider the emergence of a new kind of earth observation regime that impacts"
" how the world is observed and assessed, and that generates new spheres of interests and power struggles. Through the vantage point of GeoAI, I reflect on the current condition of"
" planetary computing, globe spanning translational computational infrastructure and evaluation networks. Based on field studies performed in one particular majority world context,"
" I reflect on the value of GeoAI in different contexts, on the unexpected traps that GeoAI produces, and what we might learn from this case for the governance of planetary-scale AI systems in the future.")
st.markdown(text)

text = ("The sections featured on this site correspond to Chapter 4 of the book. They provide context for the field notes, datasets and machine learning"
" experiments and offer nuanced details that the text omits. The final section, _Performing like an algorithm_, illustrates how multiple machine learning models,"
" some trained on the data collected in the field, succeed and fail in capturing the subtleties of the tropical landscape. These experiments aim to expand the discourse"
" within critical technology studies by examining specific algorithms in action in a particular context.")
st.markdown(text)

#----------------------------------------------------------

