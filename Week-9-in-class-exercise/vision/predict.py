from cog import BasePredictor, Input, Path # type: ignore
import os
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import sys

# 1. Add your subfolders to the system path so Python can find your logic files
sys.path.append(os.path.abspath('./face_landmark_detection'))
sys.path.append(os.path.abspath('./pose_landmark_detection'))

# 2. Import the mathematical logic you wrote!
from face_landmark_detection.detection import classify_face_direction, classify_gaze_direction
from pose_landmark_detection.detection import classify_arms

class Predictor(BasePredictor):
    def setup(self):
        """Load the models into memory to make running multiple predictions fast."""
        print("Loading models...")
        
        # Load Pose Model
        pose_model_path = './pose_landmark_detection/pose_landmarker.task'
        pose_base = python.BaseOptions(model_asset_path=pose_model_path)
        self.pose_detector = vision.PoseLandmarker.create_from_options(
            vision.PoseLandmarkerOptions(base_options=pose_base, output_segmentation_masks=False)
        )

        # Load Face Model
        face_model_path = './face_landmark_detection/face_landmarker.task'
        face_base = python.BaseOptions(model_asset_path=face_model_path)
        self.face_detector = vision.FaceLandmarker.create_from_options(
            vision.FaceLandmarkerOptions(
                base_options=face_base, 
                output_face_blendshapes=True
            )
        )

    def predict(
        self,
        image: Path = Input(description="Input image file"),
        task: str = Input(
            
            description="Which detection task do you want to run?",
            choices=["face", "pose"],
            default="pose"
        )
    ) -> str:
        """Run a single prediction on the model."""
        
        # Read the image using OpenCV (safely converting the Cog Path to a string)
        img = cv2.imread(str(image))
        if img is None:
            return "Error: Could not read image."
            
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_img)

        # Route to the correct logic based on the user's dropdown choice
        if task == "pose":
            result = self.pose_detector.detect(mp_image)
            return classify_arms(result)
            
        elif task == "face":
            result = self.face_detector.detect(mp_image)
            return "Landmark: " + classify_face_direction(result) + " " + "Blendshapes: " + classify_gaze_direction(result)