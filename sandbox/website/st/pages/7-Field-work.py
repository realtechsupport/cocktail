# GISlogics - Field work
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

stitle =  '<p style="text-align: center; font-size: 18px;">Field work</p>'
st.markdown(stitle, unsafe_allow_html=True)
st.markdown("")
st.markdown("")


text = ("If there can be no supervised machine learning nor GeoAI without labeled data, then we should attend"
" to the pathways along which the labels that link data to algorithms come to be. This is important for two"
" reasons. First, because the era of ‘post-truth’ can be used to suggest that any form of evidence is suspect."
" Second, because the concept of ground truth as it applies to spatial practices is thornier yet than in other"
" domains of AI.")
st.markdown(text)


text = ("When considering the construction of reference data for land cover evaluation in the Alas Mertajati,"
" there are more than just technical questions to address. Determining which ground conditions should be included"
" in the representation demonstrates how GeoAI can intertwine itself with local politics. The Alas Mertajati has"
" never undergone such detailed surveying with GeoAI before. The Indonesia National Geospatial Information Agency (BIG)"
" provides a formal taxonomy of land cover classes for Indonesia, and adhering to these categories would ensure"
" compatibility with future national government land management efforts. However, accepting these categories also means"
" accepting the politics embedded within them, acknowledging government control not only over land classification but"
" also how the lands are represented to the world. Our partner organization, the NGO WISNU, faced the difficult task"
" of reconciling these opposing forces. The desire for integration into the established system was just as strong as"
" the selective opposition against it. After several months of  discussions and debates, we reached a consensus on a"
" collection of land cover categories deemed relevant to the Indigenous People of Dalem Tamblingan and compatible with BIG's existing geospatial taxonomy."
" The agreed-upon categories to represent the Alas Mertajati included _water, settlements, shrubs, grass lands, homogeneous forests,"
" mixed forests, agriculture plots, open lands, mixed gardens, clove forests, agroforestry and rice paddies_."
" The only category not part of BIG's system is agroforestry, which happens to be both technically challenging and"
" politically significant, as the book describes in detail.")
st.markdown(text)

text = ("In order to represent agroforestry in this GeoAI project, WISNU and our team first compiled a database" 
" of sites for each of the categories listed. These sites were initially identified in our Planet Lab satellite imagery.")
st.markdown(text)

image = "area2_datacollection_agroforestry.png"
d = Image.open(imagepath + image)
st.image(d, width="50%", use_column_width=True)
st.caption("Sites identified as ground truth representation for land cover analysis. Dozens of sites were"
" identified for each of the categories. The circled area in the middle of the image (-8° 16' 5.555 S, 115° 4' 47.705 E) is identified as" 
" a well-structured site for agroforestry-based food production.")

#-------------------------------------------------------------------------------------------------------------------

text = ("This first list was then verified in the field. We worked with our local informant,"
" Gusti Nugurah Gde Sutarjana, to collect video documentation from specific field sites of interest."
" With the expertise of Rajif Iryadi from the Indonesian Institute of Sciences, we vetted the candidate sites"
" for appropriateness and accuracy to create a database of dozens of sites for each individual category.")
st.markdown(text)

video = "Agroforestry_20221229_023406596_silent.mp4"
video_file = open(videopath + video, 'rb')
video_bytes = video_file.read()
st.video(video_bytes)
st.caption("Agroforestry site in the Tamblingan lands surrounding the Alas Mertajati ( -8° 16' 5.555'' S, 115° 4' 47.705'' E). Video by RTS.")
#-------------------------------------------------------------------------------------------------------------------

text = ("Agroforestry plots in the vicinity of the Alas Mertajati area vary in size, ranging from small fractions of a hectare to larger plots of five hectares or more."
" Within the Tamblingan region, the agroforestry plots commonly consist of a combination of coffee, avocado, jackfruit, guava, and taro plants, along"
" with palm, clove, and banana trees. Typically, certain species dominate the plantings in the plots, with informal areas interspersed throughout.")
st.markdown(text)


text = (" In some cases, sections of the plots may be left semi-wild. There is a fluid boundary between agroforestry and mixed tropical gardens. Some of the same"
" plant species can be found in both configurations. However, mixed gardens tend to be more structured, intensively managed, and located adjacent to roadways,"
" while agroforestry sites are often surrounded by forested areas and are generally less intensively managed. Given that even local experts can disagree on the differences,"
" the distinction between these categories remains far less crisp than classification procedures would wish for. The collection of field videos here gives some insight"
" into the similarities between forest, garden, agriculture and agroforestry sites.")

c1, c2 = st.columns([2,1])
c1.markdown(text)

type = c1.selectbox("View some of the study sites.", ('Rice Paddy', 'Mixed Garden', 'Secondary Forest', 'Clove Trees', 'Agriculture'))

# Get the names of videos in the video directory
temp = [file for file in os.listdir(videopath)]
video = 'n.a.'
for item in temp:
	t = type.split(' ')
	c = str(t[0])
	if(c in item):
		video = item
		break

video_file = open(videopath + video, 'rb')
video_bytes = video_file.read()
c2.video(video_bytes)

#---------------------------------------------------------------------------------------------------------------------

