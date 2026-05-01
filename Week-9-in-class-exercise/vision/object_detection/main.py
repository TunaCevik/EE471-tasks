import os
# Suppress the MediaPipe/TensorFlow warnings in the terminal
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  
os.environ['GLOG_minloglevel'] = '2'

import cv2
import mediapipe as mp
import argparse
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Import your drawing function
from prewritten_code import visualize

def main():
    parser = argparse.ArgumentParser(description="MediaPipe Object Detection CLI")
    # Supports processing multiple images at once
    parser.add_argument("--input", type=str, nargs='+', required=True, help="Path to input image(s)")
    parser.add_argument("--output_dir", type=str, default="../results", help="Directory for output")
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # 1. Configuration
    model_path = 'object_detection.task'
    if not os.path.exists(model_path):
        print(f"Error: Model file '{model_path}' not found in the current directory.")
        return

    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.ObjectDetectorOptions(
        base_options=base_options,
        score_threshold=0.5
    )
    detector = vision.ObjectDetector.create_from_options(options)

    # 2. Execution Loop
    try:
        for image_path in args.input:
            if not os.path.exists(image_path):
                print(f"Warning: File not found '{image_path}'")
                continue

            # 3. Robust Image Loading
            numpy_image_bgr = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if numpy_image_bgr is None:
                print(f"Error reading {image_path}")
                continue
            
            # Convert to RGB for MediaPipe
            numpy_image_rgb = cv2.cvtColor(numpy_image_bgr, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_image_rgb)

            # 4. Run Object Detection
            detection_result = detector.detect(mp_image)

            # 5. Process and Visualize Output
            annotated_image_rgb = visualize(numpy_image_rgb, detection_result)

            # 6. Save the Results (Convert back to BGR for OpenCV saving)
            filename = os.path.basename(image_path)
            save_path = os.path.join(args.output_dir, f"detected_{filename}")
            
            final_bgr_image = cv2.cvtColor(annotated_image_rgb, cv2.COLOR_RGB2BGR)
            cv2.imwrite(save_path, final_bgr_image)

            # Print Terminal Summary
            print(f"\nSuccess for: {filename}")
            print(f"  - Output saved to: {save_path}")
            print(f"  - Objects found: {len(detection_result.detections)}")
            
            for i, detection in enumerate(detection_result.detections):
                cat = detection.categories[0]
                print(f"    * Object #{i+1}: {cat.category_name} ({cat.score:.2f} confidence)")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()