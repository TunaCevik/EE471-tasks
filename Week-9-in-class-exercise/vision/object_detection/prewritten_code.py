import cv2
import numpy as np

MARGIN = 10  # pixels
ROW_SIZE = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
TEXT_COLOR = (255, 0, 0)  # Red (Since we process the image in RGB space)

def visualize(image, detection_result) -> np.ndarray:
    """Draws bounding boxes on the input image and returns it."""
    
    # We create a copy of the image to avoid modifying the original data directly
    annotated_image = np.copy(image)
    
    for detection in detection_result.detections:
        # Draw bounding_box
        bbox = detection.bounding_box
        
        # SAFETY FIX: Cast coordinates to integers to prevent OpenCV TypeErrors
        start_point = (int(bbox.origin_x), int(bbox.origin_y))
        end_point = (int(bbox.origin_x + bbox.width), int(bbox.origin_y + bbox.height))
        
        cv2.rectangle(annotated_image, start_point, end_point, TEXT_COLOR, 3)

        # Draw label and score
        category = detection.categories[0]
        category_name = category.category_name
        probability = round(category.score, 2)
        result_text = f"{category_name} ({probability})"
        
        text_location = (MARGIN + int(bbox.origin_x), MARGIN + ROW_SIZE + int(bbox.origin_y))
        
        cv2.putText(annotated_image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                    FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

    return annotated_image