import os
import argparse

# STEP 1: Import the necessary modules.
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Import your chosen Colab helper function
from prewritten_code import draw_landmarks_on_image

def main():
    parser = argparse.ArgumentParser(description="MediaPipe Hand Landmark Detection")
    parser.add_argument("--input", type=str, default="../images/hand.png", help="Path to input image")
    parser.add_argument("--output_dir", type=str, default="../results", help="Directory for output")
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # STEP 2: Create a HandLandmarker object.
    model_path = 'hand_landmarker.task'
    if not os.path.exists(model_path):
        print(f"Error: Model file '{model_path}' not found in the current directory.")
        return

    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2
    )
    detector = vision.HandLandmarker.create_from_options(options)

    try:
        # STEP 3: Load the input image.
        # Note: Using your preferred Colab method. 
        # If this throws a "Failed to load" error on Linux, we must revert to cv2.imread
        print(f"Loading image from: {args.input}")
        image = mp.Image.create_from_file(args.input)

        # STEP 4: Detect hand landmarks from the input image.
        detection_result = detector.detect(image)

        # STEP 5: Process the classification result. In this case, visualize it.
        annotated_image = draw_landmarks_on_image(image.numpy_view(), detection_result)
        
        # Convert RGB to BGR for OpenCV saving (replacing Colab's cv2_imshow)
        final_image_bgr = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
        
        # Determine save path and save the file
        filename = os.path.basename(args.input)
        save_path = os.path.join(args.output_dir, f"annotated_{filename}")
        cv2.imwrite(save_path, final_image_bgr)
        
        print(f"Success! Image processed and saved to: {save_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()