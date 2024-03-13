import argparse
import json
# from pipeline_scripts.training_pipeline import *

def parse_args():
    parser = argparse.ArgumentParser(description='Convert command line arguments to config.json')
    parser.add_argument('--model_path', type=str, help='Path to the trained model')
    parser.add_argument('--google_storage_path', type=str, help='Google storage path')
    parser.add_argument('--model_name', type=str, help='Name of the model')
    parser.add_argument('--test_image_path', type=str, help='Path to the test image')
    parser.add_argument('--img_size', type=int, help='Image size (height and width)')
    parser.add_argument('--num_bands', type=int, help='Number of bands')
    parser.add_argument('--num_classes', type=int, help='Number of classes')
    parser.add_argument('--gcs_tfrecords', type=str, help='Google storage path for TFRecords')
    parser.add_argument('--class_name', type=int, help='Class name')
    parser.add_argument('--label_path', type=str, help='Path to the label raster')
    parser.add_argument('--class_optmized_model', type=int, help='Class optimized model')
    parser.add_argument('--bucket_name', type=str, help='Name of the bucket')
    parser.add_argument('--threshold_percentage', type=float, help='Threshold percentage')
    parser.add_argument('--patch_height', type=int, help='Patch height')
    parser.add_argument('--patch_width', type=int, help='Patch width')
    parser.add_argument('--batch_size', type=int, help='Batch size')
    parser.add_argument('--epochs', type=int, help='Epochs')

    return parser.parse_args()

def write_config(args, filename):
    config = {
        'model_path': args.model_path,
        'google_storage_path': args.google_storage_path,
        'model_name': args.model_name,
        'test_image_path': args.test_image_path,
        'img_size': args.img_size,
        'num_bands': args.num_bands,
        'num_classes': args.num_classes,
        'gcs_tfrecords': args.gcs_tfrecords,
        'class_name': args.class_name,
        'label_path': args.label_path,
        'class_optmized_model': args.class_optmized_model,
        'bucket_name': args.bucket_name,
        'threshold_percentage': args.threshold_percentage,
        'patch_height': args.patch_height,
        'patch_width': args.patch_width,
        'batch_size': args.batch_size,
        'epochs': args.epochs
    }

    with open(filename, 'w') as f:
        json.dump(config, f, indent=4)


args = parse_args()
write_config(args, '/home/jupyter/eval_and_pred/pipeline_scripts/config.json')
# write_config(args, './pipeline_scripts/config.json')