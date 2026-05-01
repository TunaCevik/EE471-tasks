import cv2
import mediapipe as mp
import os
import argparse
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from prewritten_code import draw_landmarks_on_image, plot_face_blendshapes_bar_graph

from detection import classify_face_direction, classify_gaze_direction

def main():
    parser = argparse.ArgumentParser(description="MediaPipe Face Landmark Detection CLI")
    parser.add_argument("--input", type=str, required=True, help="Path to the input image")
    parser.add_argument("--output_dir", type=str, default="../results", help="Directory to save the result")
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Configuration
    model_path = 'face_landmarker.task' 
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_faces=1,
        min_face_detection_confidence=0.75,
        min_face_presence_confidence=0.75,
        min_tracking_confidence=0.75,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True
    )

    detector = vision.FaceLandmarker.create_from_options(options)
    
    try:
        # 1. Load with OpenCV
        numpy_image_bgr = cv2.imread(args.input, cv2.IMREAD_COLOR)
        
        if numpy_image_bgr is None:
            print(f"Error: Could not read image at {args.input}. Check if the path is correct.")
            return

        # 2. Convert to RGB (Required for MediaPipe)
        numpy_image_rgb = cv2.cvtColor(numpy_image_bgr, cv2.COLOR_BGR2RGB)

        # 3. Create MediaPipe object from that data
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_image_rgb)

        # 4. Run detection
        detection_result = detector.detect(mp_image)

        # 5. Annotate and Save
        annotated_image = draw_landmarks_on_image(mp_image.numpy_view(), detection_result)

        filename = os.path.basename(args.input)
        output_path = os.path.join(args.output_dir, f"annotated_{filename}")

        # 6. Convert back to BGR for saving with OpenCV
        final_bgr_image = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, final_bgr_image)

        print(f"Result saved to: {output_path}")

        filename_without_ext = filename.split('.')[0]
        # 7. Process Output
        if detection_result.face_blendshapes:
            plot_path = os.path.join(args.output_dir, f"plot_{filename_without_ext}.png")
            # We pass the path so the function knows where to save it
            plot_face_blendshapes_bar_graph(detection_result.face_blendshapes[0], save_path=plot_path)
            print(f"Success: Bar chart saved to {plot_path}")

        # 8. Detection which direction face is looking at
        result_string_landmarks = classify_face_direction(detection_result)
        print(f"\n[Output Result Landmarks]: {result_string_landmarks}\n") # This will print "left", "right", or "straight"

        result_string_blends = classify_gaze_direction(detection_result)
        print(f"\n[Output Result Blendshapes]: {result_string_blends}\n") # This will print "left", "right", or "straight"

        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()