from tensorflow import keras
from tensorflow.keras import layers
import os
import tensorflow as tf
from model import get_model
from create_dataset import train_test_datasets
from model_config import CustomModel
import argparse
from eval import compute_metrics
# values


username = os.getenv("USER") or os.getenv("LOGNAME")
num_bands = 8 # 8 bands images as input 
# patch_height = 8
# patch_width = 8
# img_size = (patch_height, patch_width)
# num_classes = 23
# path = f'/home/{username}/project/trained_models/'







parser = argparse.ArgumentParser(description='Model_Name')

parser.add_argument('--model_name', type=str, default='patch_8_batch_32.hdf5',
                    help='Mention the name of model to store')

parser.add_argument('--model_dir', type=str, default= f'/home/{username}/project/trained_models/',
                    help='Mention the directory to store the model')

parser.add_argument('--patch_size', type=int, default= 8, help='Mention the patch size')

parser.add_argument('--num_classes', type=int, default= 23, help='Mention the classes to categorize')

parser.add_argument('--epochs', type=int, default= 1, help='Mention the number of epochs to train the model')

parser.add_argument('--batch_size', type=int, default= 32, help='Mention the number of batch_size to train the model')

args = parser.parse_args()

model_name = args.model_name
path = args.model_dir
patch_height = args.patch_size
patch_width = args.patch_size
num_classes = args.num_classes
train_epochs = args.epochs
train_batch_size = args.batch_size

model_name_without_extension = os.path.splitext(model_name)[0]
logs_directory = os.path.join(path, "logs")
os.makedirs(logs_directory, exist_ok=True)


img_size = (patch_height, patch_width)
# get the train and test datasets
train_dataset, val_dataset = train_test_datasets()
model = CustomModel(img_size=img_size, num_classes=num_classes, num_bands=num_bands, num_unet_layers=2).build_model()
CustomModel(img_size=img_size, num_classes=num_classes, num_bands=num_bands, num_unet_layers=2).plot_model_diagram(f"/home/{username}/project/model_artictecture.png")
# model = get_model(img_size=img_size, num_classes=num_classes, num_bands=num_bands)
model.compile(optimizer="adam", loss="categorical_crossentropy")

# metrics_results = compute_metrics(train_dataset, model.predict(train_dataset))

## callbacks and logging

# CSVLogger callback
# csv_logger = keras.callbacks.CSVLogger(os.path.join(logs_directory, f"training_logs_of_{model_name_without_extension}.csv"), append=True)

# # Additional callback for custom metrics
# custom_metrics_callback = keras.callbacks.LambdaCallback(
#     on_epoch_end=lambda epoch, logs: logs.update({
#         "class_wise_iou": metrics_results[0],
#         "class_wise_dice_score": metrics_results[1],
#         "class_wise_accuracy": metrics_results[2],
#         "class_wise_precision": metrics_results[3],
#         "class_wise_recall": metrics_results[4],
#         "mean_iou": metrics_results[5],
#         "epoch": epoch,
#         "loss": logs["loss"],
#         "val_loss": logs["val_loss"]
#     })
# )



# # Combine all callbacks
# all_callbacks = [
#     keras.callbacks.ModelCheckpoint(os.path.join(path, model_name), save_best_only=True),
#     csv_logger,
#     custom_metrics_callback
# ]



callbacks = [
    keras.callbacks.ModelCheckpoint(os.path.join(path, model_name), save_best_only=True),
    keras.callbacks.CSVLogger(os.path.join(logs_directory, f"training_logs_of_{model_name_without_extension}.csv"), append=True),  # Add CSVLogger
]

model_history = model.fit(train_dataset,
                    epochs=train_epochs,
                    callbacks=callbacks,
                    batch_size=train_batch_size,
                    validation_data= val_dataset)
model.save(path+model_name)
