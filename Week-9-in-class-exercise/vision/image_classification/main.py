import os
# Suppress the MediaPipe/TensorFlow warnings in the terminal
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  
os.environ['GLOG_minloglevel'] = '2'

import cv2
import mediapipe as mp
import argparse
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Import your matplotlib drawing function
from prewritten_code import display_batch_of_images

def main():
    parser = argparse.ArgumentParser(description="MediaPipe Image Classification CLI")
    # nargs='+' allows you to input multiple files like: --input img1.png img2.png img3.png
    parser.add_argument("--input", type=str, nargs='+', required=True, help="Path to input image(s)")
    parser.add_argument("--output_dir", type=str, default="../results", help="Directory for output")
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # 1. Configuration
    model_path = 'image_classification.task'
    if not os.path.exists(model_path):
        print(f"Error: Model file '{model_path}' not found in the current directory.")
        return

    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.ImageClassifierOptions(
        base_options=base_options, 
        max_results=4
    )
    classifier = vision.ImageClassifier.create_from_options(options)

    # Lists to hold data for the batch plot
    mp_images = []
    predictions = []

    try:
        # Loop through every image you passed in the terminal
        for image_path in args.input:
            if not os.path.exists(image_path):
                print(f"Warning: File not found {image_path}")
                continue

            # 2. Image Loading and Preprocessing (Using robust OpenCV method)
            numpy_image_bgr = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if numpy_image_bgr is None:
                continue
            
            numpy_image_rgb = cv2.cvtColor(numpy_image_bgr, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_image_rgb)

            # 3. Classify the input image
            classification_result = classifier.classify(mp_image)
            
            # Save data for the matplotlib batch grid
            mp_images.append(mp_image)
            top_category = classification_result.classifications[0].categories[0]
            predictions.append(f"{top_category.category_name} ({top_category.score:.2f})")
            
            # Print the terminal summary for this specific image
            print(f"\nResults for: {os.path.basename(image_path)}")
            for category in classification_result.classifications[0].categories:
                print(f"  - {category.category_name}: {category.score:.4f}")

        # 4. Generate and Save the Visual Batch Output
        if len(mp_images) > 0:
            save_path = os.path.join(args.output_dir, "classification_batch_result.png")
            display_batch_of_images(mp_images, predictions, save_path=save_path)
            print(f"\nSuccess! Visual batch plot saved to: {save_path}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()