import numpy as np
import matplotlib.pyplot as plt
from mediapipe.tasks.python.vision import drawing_utils
from mediapipe.tasks.python.vision import drawing_styles
from mediapipe.tasks.python import vision


def draw_landmarks_on_image(rgb_image, detection_result):
  pose_landmarks_list = detection_result.pose_landmarks
  annotated_image = np.copy(rgb_image)

  pose_landmark_style = drawing_styles.get_default_pose_landmarks_style()
  pose_connection_style = drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2)

  for pose_landmarks in pose_landmarks_list:
    drawing_utils.draw_landmarks(
        image=annotated_image,
        landmark_list=pose_landmarks,
        connections=vision.PoseLandmarksConnections.POSE_LANDMARKS,
        landmark_drawing_spec=pose_landmark_style,
        connection_drawing_spec=pose_connection_style)

  return annotated_image


# Official MediaPipe Pose Landmark Names (Indices 0 - 32)
POSE_LANDMARK_NAMES = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer",
    "right_eye_inner", "right_eye", "right_eye_outer",
    "left_ear", "right_ear", "mouth_left", "mouth_right",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_pinky", "right_pinky",
    "left_index", "right_index", "left_thumb", "right_thumb",
    "left_hip", "right_hip", "left_knee", "right_knee",
    "left_ankle", "right_ankle", "left_heel", "right_heel",
    "left_foot_index", "right_foot_index"
]

def plot_pose_visibility_bar_graph(pose_landmarks, save_path):
    """
    Plots a horizontal bar chart of the visibility confidence for all 33 pose landmarks.
    """
    # Extract the visibility scores for each of the 33 landmarks
    visibility_scores = [landmark.visibility for landmark in pose_landmarks]
    ranks = range(len(POSE_LANDMARK_NAMES))

    # Create the figure
    fig, ax = plt.subplots(figsize=(12, 10))
    bar = ax.barh(ranks, visibility_scores, color='skyblue')
    
    # Set the labels on the Y-axis to match the anatomy
    ax.set_yticks(ranks, POSE_LANDMARK_NAMES)
    ax.invert_yaxis() # Put landmark #0 (nose) at the top

    # Label each bar with the exact numerical value
    for score, patch in zip(visibility_scores, bar.patches):
        # We place the text just slightly to the right of the bar's end
        plt.text(patch.get_width() + 0.01, patch.get_y() + patch.get_height() / 2, 
                 f"{score:.4f}", va="center")

    ax.set_xlabel('Visibility Confidence (0.0 to 1.0)')
    ax.set_title("Pose Landmark Visibility Scores")
    
    # Set the X-axis limit slightly past 1.0 so the text labels fit nicely
    ax.set_xlim(0, 1.1) 
    plt.tight_layout()
    
    # Save and close to prevent memory leaks
    plt.savefig(save_path)
    plt.close()