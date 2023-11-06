# GISlogics - Performing like an algorithm
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
from streamlit_image_select import image_select

sys.path.append("/home/otbuser/all/code/")
from streamlit_helper import *
from helper import *
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
#-----------------------------------------------------------------------------------------------------

stitle =  '<p style="text-align: center; font-size: 18px;">Performing like an algorithm</p>'
st.markdown(stitle, unsafe_allow_html=True)
st.markdown("")
st.markdown("")

text = ("The operational imagery supplied by satellites in the form of geotif datasets are the ingestion"
" materials for GeoAI designed for remote sensing operations. This section will illustrate the functioning of some"
" widely deployed algorithms on satellite imagery. While the focus is on land cover classification, many of the"
" opportunities and pitfalls encountered here apply to GeoAI operations in a broader sense, and in some cases,"
" to AI in general. Experiments I performed in an attempt to represent the Alas Mertajati through the lens of AI"
" operations deliver the materials presented here, with data dependency the factor along which I organize the individual GeoAI opportunities.")
st.markdown(text)

text = ("I want to focus on three specific questions. How does the algorithm operate? What are its capabilities"
" and what are its limitations? If you tap on the gear icon of one of the algorithms below, that algorithm will "
" operate on the selected satellite image. In the case of the supervised learning algorithms, the model trained with"
" the data described earlier will evaluate the selected image. The result will be displayed next to the selected image.")
st.markdown(text)

text = ("The mapping of categorized classes generates images that make land cover classifications appear as graphical objects."
" However, the classification process establishes artificial boundaries based on statistical definitions, implying a landscape"
" configuration that is more  organized than it actually is. This classification, coupled with the colorization intended to enhance"
" readability, further contributes to the fabrication and distortion that have long been acknowledged in"
" map-making. It is important to keep this fictionalization effect in mind when viewing any land cover map.")
st.markdown(text)

text = ("_Arithmetic Operators_")
st.markdown(text)

text = ("The NDVI (_Normalized Difference Vegetation Index_) is a widely employed metric in GeoAI for estimating"
" the density of plant growth on land. It involves a straightforward arithmetic calculation using the red and"
" near-infrared bands, eliminating the need for training data like the other algorithms discussed later."
" As a result, NDVI and similar arithmetic operations are appealing for land surveys. However, these easy to use"
" operators have limitations.")
st.markdown(text)

text = ("NDVI lacks the differentiation needed for capturing the vegetation variations commonly"
" found in agroforestry sites. Additionally, agroforestry sites are typically surrounded by various other"
" types of vegetation, such as agricultural plots, gardens, and forested areas, making the robust and"
" convenient NDVI too limited for this task, as you can see below, if you tap on the NDVI option.")
st.markdown(text)
# ----------------------------------------------------------------------------------------------------------------------------------

# Sample data
collection = [imagepath+"area2_v1.png", imagepath+"area2_v2.png", imagepath+"area2_v4.png", imagepath+"area2_v5.png"]
t = "Select an area"

# Arithmetic operations ------------------------------------------------------------------------------------------------------------

# Select an image
img = image_select(label = t, images = collection,)
imageinfo = img.split('/')
imagename_png = str(imageinfo[-1])
inputimage = imagename_png.split('.png')[0] + '.tif'

# ----------------------------------------------------------------------------------------------------------------------------------
if st.button(':gear: NDVI :gear:'):
	inputimage_display = imagename_png
	outputimage = inputimage.split(".tif")[0] + "_ndvi.png"
	grey_outputimage = inputimage.split('.tif')[0] + "_ndvi_grey.png"
	jet_outputimage = inputimage.split('.tif')[0] + "_ndvi_jet.png"
	green_outputimage = inputimage.split('.tif')[0] + "_ndvi_green.png"
	colormaps = {"grey" : grey_outputimage, "jet" : jet_outputimage, "green" : green_outputimage}

	ndvi_superdove(imagepath, datapath, inputimage, outputimage)

	for color, oimage in colormaps.items():
		do_colormap(outputimage, oimage, datapath, color)

	dd = []
	dd.append(imagepath + inputimage_display )
	for oimage in colormaps.values():
		dd.append(datapath + oimage)

	print(dd)
	c1, c2, c3, c4 = st.columns(4)
	c1.image(dd[0], use_column_width=True)
	c2.image(dd[1], use_column_width=True)
	c3.image(dd[2], use_column_width=True)
	c4.image(dd[3], use_column_width=True)

	text = ("The image on the left displays the RGB representation of the selected area."
	" The subsequent image on the right presents the NDVI in gray scale, with lighter tones indicating a greater"
	" abundance of vegetation. The third image utilizes a red scale system to depict the same data, where brighter"
	" red hues correspond to areas with higher vegetation levels. The final image represents the NDVI data using a"
	" green scale. The consistent visual appearance across all mappings shows that the capabilities"
	" of the NDVI algorithm are limited to distinguishing lakes and settlements from vegetation; it can not detect clouds," 
	" and it does not have the capacity to differentiate between different types of vegetation.")
	st.markdown(text)

# ----------------------------------------------------------------------------------------------------------------------------------
st.markdown('##')
text = ("_Shallow Learners_")
st.markdown(text)

text = ("Machine learning algorithms use data to train models. They learn the characteristics of target classes from training samples"
" and to identify these learned characteristics in new datasets. Shallow learners is the term used to describe supervised machine learning"
" algorithms that have fewer parameters and lower dependency on training data size. This class includes random forests, support vector machines"
" and small neural networks. GeoAI has relied on these classifiers for decades for land cover analysis. Here, all implementations here are based"
" on the opensource Orfeo geospatial analysis libraries. As the book describes, a new generation of deep neural networks are entering the fray and in some cases"
" delivering significant improvements in classification accuracy. Yet, shallow learners can be quite powerful, and offer unique advantages as we will see.")
st.markdown(text)

text = ("The training process depends on representative samples that cover the distribution of the desired category. If the chosen samples are"
" inadequate or the dataset is too small, the classification results will be compromised. Complex data categories, such as agroforestry and rice paddies,"
" present serious challenges for machine learning systems. The recent success in image classification owes much to well-organized"
" training data applied to well-defined categories. When algorithms are trained and tested on such well-structured datasets,"
" they can effectively discriminate between objects. Differentiating between cars, trains, and airplanes, for example, is a relatively"
" straightforward task. Even discerning between similar-looking car models poses no problem for a well-designed classifier."
" Automobiles do not shape-shift. They are uniform and predictable compared to agroforestry plots.")
st.markdown(text)

text = ("In order to illustrate these issues, I will describe how some established shallow learners respond to the task of producing"
" a land cover classification map in the Alas Mertajati.")
st.markdown(text)
# --------------------------------------------------------------------------

text = ("_Random Forests_")
st.markdown(text)

text=("The random forest classifier is a classic algorithm. The term forest stems from the fact that the classifier employs an ensemble of simpler"
" base elements to do its work. These base elements are decision rules extracted from the data features. The rules themselves are basic, such as"
" “if the datapoint is equal to 0, apply the color red, else apply the color green”. However, by combining multiple simple decisions into larger structures,"
" hence the term trees, more intricate decision conditions can be created. The random forest classifier creates numerous individual decision tree components"
" and lets them all contribute in solving a problem. Then it takes a vote amongst the individual decision trees and picks the solution shared by the majority"
" of decision trees in categorical classification tasks. Random forests do make use of a randomness when the data is distributed to the various tree elements."
" Each time you train a random forest classifier, you get a different result, though the differences are often small.")
st.markdown(text)

text = ("The random forest classifier is widely employed in remote sensing due to the accuracy of its classifications and the comparative simplicity"
" of the underlying algorithm. But how will the random forest classifier respond to complex land cover features of the Alas Mertajati?")
st.markdown(text)


# Select an image
t = t  + " "
img = image_select(label = t, images = collection,)
imageinfo = img.split('/')
imagename_png = str(imageinfo[-1])
inputimage = imagename_png.split('.png')[0] + '.tif'

# ---------------------------------------------------------------------------

# Load model and perform classification
c1,c2,c3 = st.columns([2,1,1])
cm = c2.selectbox("landscape features rf", ('all features', 'agroforestry', 'settlements', 'rice paddies'), label_visibility = 'collapsed')

if c1.button(':gear: Random Forests :gear:'):
	outputimage = inputimage.split(".tif")[0] + "_rf.png"
	c_outputimage = inputimage.split(".tif")[0] + "_rf_color.png"
	model = "model_rf_15-07-2023-13-59.model"
	do_classification(inputimage, imagepath, outputimage, model, datapath, modelpath)

	if(cm == 'all features'):
		colormap = "colormap_FOSS4G2023_paper.txt"
	elif(cm == 'agroforestry'):
		colormap = "colormap_FOSS4G2023_paper_agroforestry.txt"
	elif(cm == 'settlements'):
		colormap = "colormap_FOSS4G2023_paper_settlements.txt"
	elif(cm == 'rice paddies'):
		colormap = "colormap_FOSS4G2023_paper_ricepaddies.txt"
	else:
		colormap = "colormap_FOSS4G2023_paper.txt"

	do_colormap(outputimage, c_outputimage, datapath, colormap)

	rf = []
	rf.append(imagepath + imagename_png)
	rf.append(datapath + c_outputimage)
	rf.append(imagepath + "legend.png")
	c1, c2, c3 = st.columns([2,2,1])
	c1.image(rf[0], use_column_width=True)
	c2.image(rf[1], use_column_width=True)
	c3.image(rf[2], use_column_width=True)

	text = ("This particular random forest model (trees:100, tree depth:5, min samples per tree:1) seems to capture many of the land cover categories reasonably well –"
	" until one considers the details. While rice paddies and agroforestry areas are detected, both categories exhibit"
	" numerous false positive results – indicating their presence where they do not actually occur and underestimating the extent of agroforestry."
	" The protected forest on the slopes of the volcano Gunung Lesung is not properly represented , with large segments being inadequately"
	" categorized. The forest here is almost contiguous. Furthermore, the representation of settlements appears inadequate. These"
	" qualitative observations can be quantified by consulting the f-scores, which combine precision and recall, as discussed"
	" in detail in the book. Moreover, the overall performance, captured by the kappa score is less than 60%, and so this algorithm"
	" disappoints overall in its ability to properly differentiate the tropical landscape of the Alas Mertajati."
	" There is considerable variation in the output of the random forest models, and some hardly capture agroforestry at all."
	" In all cases, the overall performance as measured by the kappa index inadequate. However, the algorithm has a small footprint"
	" and inference is very fast as you experienced on this page.")
	st.markdown(text)
#-----------------------------------------------------------------------------

text = ("_Support Vector Machines_")
st.markdown(text)

text = ("The support vector machine classifier (SVM) separates data into different classes by finding an optimal dividing line between given sets."
" In two dimensions, this process is easy to visualize. Picture a set of red dots on one side of a page and a set of blue points on the other side."
" You can position a straight line on the page “just so” to maximize the distance between the line and each set of dots. However, when dealing with"
" non-linear data that cannot be separated by a straight line in a two-dimensional space, a different approach is required. This involves “projecting” "
" the data into a higher dimension to identify a suitable cutting path through the data. This abstraction may sound peculiar, and indeed it is. This is"
" where the concept of a hyperplane comes into play. In higher dimensions, the hyperplane replaces the line, becoming a surface in two dimensions."
" Remarkably, SVM performs well in many dimensions. It utilizes a technique called the kernel trick to operate efficiently in a higher-dimensional feature"
" space without the need to compute the data's coordinates in that space. This makes SVM an efficient classification machine. In the realm of GeoAI analysis,"
" SVM is a core component due to its ability to efficiently handle multi-class classification, which aligns perfectly with our requirements."
" However, SVM can perform poorly when data features are vague and overlapping, as is the case in the Alas Mertajati landcover dataset.") 
st.markdown(text)

# Select an image
t = t  + " "
img = image_select(label = t, images = collection,)
imageinfo = img.split('/')
imagename_png = str(imageinfo[-1])
inputimage = imagename_png.split('.png')[0] + '.tif'

# Load model and perform classification
c1,c2,c3 = st.columns([2,1,1])
cm = c2.selectbox("landscape features svm", ('all features', 'agroforestry', 'settlements', 'rice paddies'), label_visibility = 'collapsed')

if c1.button(':gear: Support Vector Machine :gear:', help = 'Wait a few seconds for the algorithm to run its course'):
	outputimage = inputimage.split(".tif")[0] + "_svm.png"
	c_outputimage = inputimage.split(".tif")[0] + "_svm_color.png"
	model = "model_svm_15-07-2023-16-20.model"
	do_classification(inputimage, imagepath, outputimage, model, datapath, modelpath)

	if(cm == 'all features'):
		colormap = "colormap_FOSS4G2023_paper.txt"
	elif(cm == 'agroforestry'):
		colormap = "colormap_FOSS4G2023_paper_agroforestry.txt"
	elif(cm == 'settlements'):
		colormap = "colormap_FOSS4G2023_paper_settlements.txt"
	elif(cm == 'rice paddies'):
		colormap = "colormap_FOSS4G2023_paper_ricepaddies.txt"
	else:
		colormap = "colormap_FOSS4G2023_paper.txt"


	do_colormap(outputimage, c_outputimage, datapath, colormap)

	svm = []
	svm.append(imagepath + imagename_png)
	svm.append(datapath + c_outputimage)
	svm.append(imagepath + "legend.png")
	c1, c2, c3 = st.columns([2,2,1])
	c1.image(svm[0], use_column_width=True)
	c2.image(svm[1], use_column_width=True)
	c3.image(svm[2], use_column_width=True)

	text = ("Upon initial inspection, this SVM model(kernel: linear, C value: 1.0) appears to differentiate our desired land cover categories with more nuance"
	" than the Random Forest algorithm. Furthermore, SVM demonstrates a more discerning approach in handling agroforestry, differentiating"
	" with more grace the competing and overlapping categories of mixed gardens and secondary forests. It also exhibits superior performance"
	" in identifying larger rice paddy fields. However, SVM is not flawless. This is evident in the presence of spurious falsely identified"
	" agroforestry locations around Lake Tamblingan, for instance. It seems that any human intervention in forested areas generates a similar"
	" signature for the algorithm. The quantitative results present a clear picture. Agroforestry achieves in training an f1-score of 62% only."
	" Nonetheless, the kappa index reaches 72% across all categories, which is a respectable result. In fact, SVM can rival its data hungry counterparts,"
	" such as neural networks, while requiring comparatively modest computational resources and significantly less training data."
	" The significance of these factors is discussed in more detail in the book.")
	st.markdown(text)

#-----------------------------------------------------------------------------

text = ("_Neural Networks_")
st.markdown(text)

text = ("Neural networks are the newest class of algorithms applied to classification tasks. As in other fields, such as language"
" translation, speech synthesis, and most recently, text and image generation, neural networks have demonstrated superior results."
" The book describes in detail the procedures used by neural networks to achieve this new level of performance, including the all-important"
" back-propagation optimization method. Neural networks have been so successful at previously challenging tasks that they are now considered"
" candidate material for the ultimate goal of AI, Artificial General Intelligence. For that reason alone, it makes sense to compare a neural"
" network-based classification of the Alas Mertajati with the standard models described above. To be clear, the neural network deployed"
" here is a comparatively shallow model with only two hidden layers.")
st.markdown(text)


if st.button('Compare Algorithms'):

	rf_area2_png = "area2_0530_2022_8bands_15-07-2023-13-59_raster_classified_color_rf_sm.jpg"
	svm_area2_png = "area2_0530_2022_8bands_15-07-2023-16-20_raster_classified_color_svm_sm.jpg"
	nn_area2_png =  "area2_0530_2022_8bands_28-11-2022-22-30_ann_sm.jpg"

	all = []
	all.append(imagepath + rf_area2_png)
	all.append(imagepath + svm_area2_png)
	all.append(imagepath + nn_area2_png)

	c1, c2, c3 = st.columns([1,1,1])
	c1.image(all[0], use_column_width=True)
	ctext = '<p style="font-size: 12px;">Random Forest</p>'
	c1.caption(ctext, unsafe_allow_html=True)

	c2.image(all[1], use_column_width=True)
	ctext = '<p style="font-size: 12px;">Support Vector Machine</p>'
	c2.caption(ctext, unsafe_allow_html=True)

	c3.image(all[2], use_column_width=True)
	ctext = '<p style="font-size: 12px;">Neural Network</p>'
	c3.caption(ctext, unsafe_allow_html=True)


	text = ("The three images show the output of the three classification approaches operating on the Alas Mertajati dataset."
	" Given the radically different approaches deployed by these algorithms, it is surprising that the produce such similar results."
	" The neural network deployed here is a comparatively shallow model with only two hidden layers. Nonetheless, the neural network"
	" was still able to capture most of the intricacies of the landscape. Overall, however, the neural network fails, similar to the"
	" random forest algorithm, in succinctly differentiating agroforestry from forested areas, in particular around Gunung Lesung."
	" It also overestimates the distribution of agroforestry plots, inconveniently suggesting that that protected forest areas south of Lake Buyan are"
	" misused for food production. While the results from support vector machine and random forest algorithms here are likely as good"
	" as they can be, the output of the neural network algorithm will improve with a deeper network. However, deep neural networks require"
	" much more training data and much more computing power, both of which are in short supply. Which is the best algorithm? The answer will depend"
	" on what we want to optimize. The book describes in more detail the tradeoffs between expensive deep GeoAI and cheap minimalist GeoAI,"
	" how those tradeoffs articulate themselves differently in different contexts, and why those observations might be useful for the governance"
	" of powerful AI systems in the future.")
	st.markdown(text)
#-----------------------------------------------------------------------------
