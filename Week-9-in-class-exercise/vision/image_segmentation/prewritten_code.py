import numpy as np
import cv2

def create_segmentation_mask(rgb_image, segmentation_result):
    """Generates a solid white foreground and gray background mask."""
    # Squeeze removes unnecessary dimensions from the mask array
    category_mask = np.squeeze(segmentation_result.category_mask.numpy_view())
    
    # 0 is usually the background, anything > 0.1 is considered the subject
    condition = category_mask > 0.1
    
    # Create solid color canvases
    fg_image = np.zeros(rgb_image.shape, dtype=np.uint8)
    fg_image[:] = (255, 255, 255) # White foreground
    
    bg_image = np.zeros(rgb_image.shape, dtype=np.uint8)
    bg_image[:] = (192, 192, 192) # Gray background
    
    # Combine them based on the AI's mask
    return np.where(condition[..., None], fg_image, bg_image)

def create_blurred_background(rgb_image, segmentation_result):
    """Keeps the subject sharp but heavily blurs the background."""
    category_mask = np.squeeze(segmentation_result.category_mask.numpy_view())
    condition = category_mask > 0.1
    
    # Create a completely blurred version of the original image
    blurred_image = cv2.GaussianBlur(rgb_image, (55, 55), 0)
    
    # Paste the sharp subject over the blurred background
    return np.where(condition[..., None], rgb_image, blurred_image)