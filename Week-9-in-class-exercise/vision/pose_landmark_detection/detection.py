def classify_arms(detection_result) -> str:
    """
    Analyzes pose landmarks to determine if arms are raised.
    Output: "left", "right", "both", or "None"
    """
    if not detection_result.pose_landmarks:
        return "None"

    # Grab the skeleton for the first person detected
    landmarks = detection_result.pose_landmarks[0]
    
    # Extract the Y-coordinates (vertical height)
    # MediaPipe Indices: Left Shoulder(11), Right Shoulder(12), Left Wrist(15), Right Wrist(16)
    left_shoulder_y = landmarks[11].y
    left_wrist_y = landmarks[15].y
    
    right_shoulder_y = landmarks[12].y
    right_wrist_y = landmarks[16].y
    
    # Check if wrists are ABOVE shoulders (meaning the Y value is SMALLER)
    # Note: MediaPipe's "Left" is the person's physical left
    left_arm_up = left_wrist_y < left_shoulder_y
    right_arm_up = right_wrist_y < right_shoulder_y
    
    if left_arm_up and right_arm_up:
        return "both"
    elif left_arm_up:
        return "left"
    elif right_arm_up:
        return "right"
    else:
        return "None"