import os
import cv2
import mediapipe as mp
import argparse
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Import your drawing and mask functions
from prewritten_code import draw_landmarks_on_image, plot_pose_visibility_bar_graph

from detection import classify_arms

def main():
    parser = argparse.ArgumentParser(description="MediaPipe Pose Landmark Detection CLI")
    # Supports processing multiple images at once
    parser.add_argument("--input", type=str, nargs='+', required=True, help="Path to input image(s)")
    parser.add_argument("--output_dir", type=str, default="../results", help="Directory for output")
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # 1. Configuration
    model_path = 'pose_landmarker.task'
    if not os.path.exists(model_path):
        print(f"Error: Model file '{model_path}' not found in the current directory.")
        return

    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=False
    )
    detector = vision.PoseLandmarker.create_from_options(options)

    # 2. Execution Loop
    try:
        for image_path in args.input:
            if not os.path.exists(image_path):
                print(f"Warning: File not found '{image_path}'")
                continue

            # 3. Robust Image Loading (BGR -> RGB)
            numpy_image_bgr = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if numpy_image_bgr is None:
                print(f"Error reading {image_path}")
                continue
            
            numpy_image_rgb = cv2.cvtColor(numpy_image_bgr, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_image_rgb)

            # 4. Run Pose Detection
            detection_result = detector.detect(mp_image)
            filename = os.path.basename(image_path)
            filename_no_ext = os.path.splitext(filename)[0]

            print(f"\nProcessing: {filename}")

            if not detection_result.pose_landmarks:
                print("  - No poses detected in this image.")
                continue

            # 5. Process Output A: The Skeleton
            annotated_image_rgb = draw_landmarks_on_image(numpy_image_rgb, detection_result)
            skeleton_save_path = os.path.join(args.output_dir, f"{filename_no_ext}_skeleton.png")
            cv2.imwrite(skeleton_save_path, cv2.cvtColor(annotated_image_rgb, cv2.COLOR_RGB2BGR))
            print(f"  - Skeleton saved to: {skeleton_save_path}")

            # Assuming you have your detection_result in main.py...
            if detection_result.pose_landmarks:
                # Pass the first detected person's landmarks
                graph_path = os.path.join(args.output_dir, f"{filename_no_ext}pose_visibility_graph.png")
                plot_pose_visibility_bar_graph(detection_result.pose_landmarks[0], graph_path)
                print(f"Graph saved to {graph_path}")
            
            # Dedect which arm is raised
            result_string = classify_arms(detection_result)
            print(f"\n[Output Result]: {result_string}\n") # This will print "left", "right", "both", or "None"
                
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()