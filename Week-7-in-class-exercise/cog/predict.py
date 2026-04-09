import os
# Saves the model weights in the current directory
os.environ["TORCH_HOME"] = "."

import torch
from cog import BasePredictor, Input, Path
from PIL import Image
from torchvision import models

# Using the pre-trained ResNet50 weights from ImageNet
WEIGHTS = models.ResNet50_Weights.IMAGENET1K_V1

class Predictor(BasePredictor):
    def setup(self):
        """Load the model into memory once to make it fast"""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = models.resnet50(weights=WEIGHTS).to(self.device)
        self.model.eval()

    def predict(self, image: Path = Input(description="Image to classify")) -> dict:
        """Process the image and return the top 3 breed guesses"""
        # Open and convert image to RGB
        img = Image.open(image).convert("RGB")
        
        # Apply standard ResNet transforms (resize, crop, normalize)
        transform = WEIGHTS.transforms()
        input_tensor = transform(img).unsqueeze(0).to(self.device)
        
        # Run the model
        with torch.no_grad():
            preds = self.model(input_tensor)
            
        # Get the top 3 results with probabilities
        top3 = preds[0].softmax(0).topk(3)
        categories = WEIGHTS.meta["categories"]
        
        # Return a dictionary of {Breed: Confidence}
        return {categories[i]: p.detach().item() for p, i in zip(*top3)}