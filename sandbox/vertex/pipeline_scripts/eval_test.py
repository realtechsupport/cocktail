import rasterio
from rasterio.mask import mask
import geopandas as gpd
from shapely.geometry import mapping
import tensorflow as tf
import time
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns
from pipeline_scripts.prediction import *
import json

def load_config(file_path):
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config

def compute_metrics(y_true, y_pred):
    '''
    Computes IOU and Dice Score.

    Args:
        y_true (tensor) - ground truth label map
        y_pred (tensor) - predicted label map
    '''

    class_wise_iou = []
    class_wise_dice_score = []
    class_wise_accuracy = []
    class_wise_precision = []
    class_wise_recall = []

    smoothening_factor = 0.00001

    for i in np.unique(y_true)[1:]:
        intersection = np.sum((y_pred == i) * (y_true == i))
        y_true_area = np.sum((y_true == i))
        y_pred_area = np.sum((y_pred == i))
        combined_area = y_true_area + y_pred_area

        iou = (intersection + smoothening_factor) / (combined_area - intersection + smoothening_factor)
        class_wise_iou.append(iou)

        dice_score =  2 * ((intersection + smoothening_factor) / (combined_area + smoothening_factor))
        class_wise_dice_score.append(dice_score)

        # Accuracy
        accuracy = np.sum((y_pred == i) & (y_true == i)) / np.sum(y_true == i)
        class_wise_accuracy.append(accuracy)

        # Precision
        precision = intersection / (y_pred_area + smoothening_factor)
        class_wise_precision.append(precision)

        # Recall
        recall = intersection / (y_true_area + smoothening_factor)
        class_wise_recall.append(recall)

    # Mean IOU
    mean_iou = np.mean(class_wise_iou)

    return class_wise_iou, class_wise_dice_score,class_wise_accuracy, class_wise_precision, class_wise_recall, mean_iou

if __name__ == "__main__":
    config = load_config('./pipeline_scripts/config.json')

    model_path = config.get("model_path")
    # model_path = "eval_and_pred/trained_model/patch_h8_w8_batch_32_on_0530_2022.hdf5"
    IMAGE_CHANNELS = config.get("num_bands")  # 8 bands images as input

    model = keras.models.load_model(model_path)
    input_shape = model.layers[0].input_shape

    PATCH_HEIGHT = input_shape[0][-3]
    PATCH_WIDTH = input_shape[0][-2]

    test_image_path = config.get("test_image_path")

    predicted_array = prediction_function_img(test_image_path)

    label_path = config.get("label_path")
    ground_truth = clip_tiff(label_path)

    def resize_img(image,label):
        image = tf.image.resize_with_crop_or_pad(image, label.shape[0], label.shape[1])
        return image, label

    def process_input(image, label):
        tensor_image = tf.convert_to_tensor(image)
        tensor_image = tf.expand_dims(tensor_image,-1)
        tensor_label = tf.convert_to_tensor(label)
        tensor_label = tf.transpose(tensor_label, perm=[1, 2, 0])

        if tensor_label.shape != tensor_image.shape:
            tensor_image, tensor_label = resize_img(tensor_image, tensor_label)

        tensor_image = tf.squeeze(tensor_image)
        tensor_label = tf.squeeze(tensor_label)

        return tensor_image.numpy().astype(int), tensor_label.numpy().astype(int)

    resized_predicted_array, new_ground_truth = process_input(predicted_array, ground_truth)

    new_boolean_mask = new_ground_truth != 0

    new_predict = np.where(new_boolean_mask,resized_predicted_array,0)

    flattened_array = np.ravel(new_predict).astype(int)
    result = np.bincount(flattened_array)

    # Generate x-axis values (unique integers in the input array)
    x_values = np.arange(len(result))

    unique_values = np.unique(new_predict)

    unique_values_ground_truth = np.unique(new_ground_truth)

    class_wise_iou, class_wise_dice_score, class_wise_accuracy, class_wise_precision, class_wise_recall, mean_iou = compute_metrics(new_ground_truth, new_predict)

    print("Class-wise IOU:", class_wise_iou)
    print("Class-wise Dice Score:", class_wise_dice_score)
    print("Class-wise Accuracy:", class_wise_accuracy)
    print("Class-wise Precision:", class_wise_precision)
    print("Class-wise Recall:", class_wise_recall)
    print("Mean IOU:", mean_iou)
