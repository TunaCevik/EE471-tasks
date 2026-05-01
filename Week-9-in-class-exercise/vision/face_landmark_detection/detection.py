def classify_face_direction(detection_result) -> str:
    """
    Analyzes face landmarks to determine looking direction.
    Output: "left", "right", or "straight"
    """
    if not detection_result.face_landmarks:
        return "None"

    # Grab the face mesh for the first person detected
    landmarks = detection_result.face_landmarks[0]

    # Extract the X-coordinates (horizontal position)
    # MediaPipe Indices: Nose Tip(1), Left Edge of Face(234), Right Edge of Face(454)
    nose_x = landmarks[1].x
    left_side_x = landmarks[234].x
    right_side_x = landmarks[454].x

    # Calculate the exact center between the left and right edges
    face_width = right_side_x - left_side_x
    center_x = left_side_x + (face_width / 2)

    # Define a "deadzone" threshold (15% of the face width). 
    # If the nose is inside this zone, they are looking straight.
    threshold = face_width * 0.15

    # Determine direction based on screen left/right
    if nose_x < (center_x - threshold):
        return "left"
    elif nose_x > (center_x + threshold):
        return "right"
    else:
        return "straight"
    

def classify_gaze_direction(detection_result) -> str:
    """
    Analyzes face blendshapes (muscle movements) to determine eye gaze direction.
    """
    if not detection_result.face_blendshapes:
        return "None"

    # Grab the blendshapes for the first person detected
    blendshapes = detection_result.face_blendshapes[0]
    
    # We will pull out the specific scores we saw in your graph!
    look_left_score = 0.0
    look_right_score = 0.0
    
    for category in blendshapes:
        # Looking Left (Person's perspective)
        if category.category_name == "eyeLookOutLeft" or category.category_name == "eyeLookInRight":
            look_left_score += category.score
            
        # Looking Right (Person's perspective)
        elif category.category_name == "eyeLookOutRight" or category.category_name == "eyeLookInLeft":
            look_right_score += category.score

    # We add the scores of both eyes together. If the combined score is higher 
    # than 0.8 (meaning both eyes are strongly looking that way), we trigger it!
    if look_left_score > 0.8:
        return "left"
    elif look_right_score > 0.8:
        return "right"
    else:
        return "straight"