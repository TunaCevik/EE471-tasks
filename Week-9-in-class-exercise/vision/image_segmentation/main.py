import os
# Suppress the MediaPipe/TensorFlow warnings in the terminal
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  
os.environ['GLOG_minloglevel'] = '2'

import cv2
import mediapipe as mp
import argparse
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Import your optimized numpy helper functions
from prewritten_code import create_segmentation_mask, create_blurred_background

def main():
    parser = argparse.ArgumentParser(description="MediaPipe Image Segmentation CLI")
    # Supports processing multiple images at once
    parser.add_argument("--input", type=str, nargs='+', required=True, help="Path to input image(s)")
    parser.add_argument("--output_dir", type=str, default="../results", help="Directory for output")
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # 1. Configuration
    model_path = 'selfie_segmenter.task'
    if not os.path.exists(model_path):
        print(f"Error: Model file '{model_path}' not found in the current directory.")
        return

    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.ImageSegmenterOptions(
        base_options=base_options,
        output_category_mask=True
    )

    # 2. Initialize the Segmenter
    with vision.ImageSegmenter.create_from_options(options) as segmenter:
        
        # Loop through every image you passed in the terminal
        for image_path in args.input:
            if not os.path.exists(image_path):
                print(f"Warning: File not found '{image_path}'")
                continue

            try:
                # 3. Robust Image Loading (OpenCV -> RGB)
                numpy_image_bgr = cv2.imread(image_path, cv2.IMREAD_COLOR)
                if numpy_image_bgr is None:
                    print(f"Error reading {image_path}")
                    continue
                
                numpy_image_rgb = cv2.cvtColor(numpy_image_bgr, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_image_rgb)

                # 4. Execute Segmentation (Only done ONCE per image)
                segmentation_result = segmenter.segment(mp_image)
                
                # 5. Process Outputs using Helper Functions
                mask_image_rgb = create_segmentation_mask(numpy_image_rgb, segmentation_result)
                blur_image_rgb = create_blurred_background(numpy_image_rgb, segmentation_result)

                # 6. Save the Results (Convert back to BGR for OpenCV)
                filename = os.path.basename(image_path)
                filename_no_ext = os.path.splitext(filename)[0]

                mask_save_path = os.path.join(args.output_dir, f"{filename_no_ext}_mask.png")
                blur_save_path = os.path.join(args.output_dir, f"{filename_no_ext}_blur.png")

                cv2.imwrite(mask_save_path, cv2.cvtColor(mask_image_rgb, cv2.COLOR_RGB2BGR))
                cv2.imwrite(blur_save_path, cv2.cvtColor(blur_image_rgb, cv2.COLOR_RGB2BGR))

                print(f"\nSuccess for: {filename}")
                print(f"  - Mask saved to: {mask_save_path}")
                print(f"  - Blur saved to: {blur_save_path}")

            except Exception as e:
                print(f"An error occurred while processing {image_path}: {e}")

if __name__ == "__main__":
    main()