# GISlogics - main
# 4 - Banana-Coffee-Taro
# https://github.com/realtechsupport/cocktail/blob/main/code/otb_raster_classify_with_model.py

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
import folium
from streamlit_folium import st_folium

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
# https://fonts.google.com/specimen/Hina+Mincho?category=Serif
# https://fonts.google.com/specimen/Fenix?category=Serif
# https://fonts.google.com/specimen/Piazzolla?category=Serif
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

stitle =  '<p style="text-align: center; font-size: 18px;">Banana, Coffee, Taro</p>'
st.markdown(stitle, unsafe_allow_html=True)
st.markdown("")
st.markdown("")


text = ("The Planetary Computing vector of GeoAI operates across the globe, and it impacts different regions and peoples in different"
" ways. This text examines some of the issues that arise when GeoAI operates in the majority world, specifically in the Indonesian"
" Archipelago and the Island of Bali.")
st.markdown(text)
#----------------------------------------------------------------------------------------------------------------------------------
c1,c2,c3 = st.columns([1,14,1])
loc = [-8.257383, 115.096541]
tiletype = "cartodbpositron"	#"OpenStreetMap"
icon = folium.features.CustomIcon(imagepath + "location-sign.png", icon_size=(18,18))
map = folium.Map(location = loc, tiles = tiletype, zoom_start = 5)
folium.Marker(loc, popup = "Bali", icon=icon).add_to(map)

with c2:
	st_data = st_folium(map, height = 400, width = 800)
	st.caption("The Indonesian Archipelago and the island of Bali.")

st.markdown("\n\n")

text = ("Bali is a small Island. On a map of Southeast Asia you can find Bali south of the Philippines, north of Australia, east of Java and"
" west of Lombok. Bali is part of the vast Indonesian archipelago covering approximately 2 million km2 and encompassing over 17’000 individual"
" islands, of which only about a third are inhabited . Indonesia is one of the world’s most populous countries, yet it includes vast areas that"
" are sparsely inhabited, including wilderness, and boasts a high level of biodiversity . Indonesia's history is long and complex, with"
" centuries of exposure to Hinduism and Buddhism, as well as decades of colonial rule under the Dutch, who recognized the country's"
" independence only several years after its formal declaration in 1945")
st.markdown(text)
#------------------------------------------------------------------------------------------------------------------------------------


image = "Bali_map_72dpi.jpg"
d = Image.open(imagepath + image)
st.image(d, width="50%", use_column_width=True)
st.caption("The island of Bali and the project study site in Central Bali.")


text = ("Indonesia is the third largest democracy in the world , and the largest Muslim-majority democracy. Unlike other parts of Indonesia"
" where Islam is the dominant religion, Bali maintains a Hindu-majority. Bali’s traditional arts, natural resources and tropical climate"
" establish it as a primer travel destination for visitors from Indonesia and abroad, contributing to its status as one of the wealthiest"
" regions in the archipelago. ")
st.markdown(text)

text = ("Since the 1930s, Bali experienced waves of exploitative activities. The 1932 documentary _Virgins of Bali_"
" featured scenes of topless Balinese women at a time when nudity of white women was banned in Hollywood. The accessible exoticism that attracted visitors and artists to the island also drew the interest of"
" two pioneers of early AI. The ground-breaking visual anthropology project by Margret Mead and Gregory Bateson, _Balinese Character:"
" A Photographic Analysis_, deployed film and photography to represent life in the village of Bayung Gede in Central Bali. Both Mead and Bateson"
" later played significant roles in contributing to the agenda of Second Order Cybernetics, a project that placed a distinct emphasis on the"
" social dimensions of control technologies. Returning to Bali, as this project does, is  an opportunity to revisit a particular thread of AI"
" history and contemplate how the generation of information technologies, and in particular GeoAI, might consider the past in crafting the future.")
st.markdown(text)


image = "area2_0530_2022_8bands_72dpi.jpg"
d = Image.open(imagepath + image)
st.image(d, width="50%", use_column_width=True)
st.caption("A satellite image of the Alas Mertajati in Central Bali. Image source Planet Labs, Superdove, May 30, 2022.")
#---------------------------------------------------------------------------------------------------
