import torch
from torch import nn
from cog import BasePredictor, Input, Path
from PIL import Image
from torchvision.transforms import ToTensor, Resize, Grayscale, Compose

class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(28*28, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 10)
        )

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits

classes = [
    "T-shirt/top", "Trouser", "Pullover", "Dress", "Coat",
    "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"
]

class Predictor(BasePredictor):
    def setup(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = NeuralNetwork()
        self.model.load_state_dict(torch.load("model.pth", map_location=self.device, weights_only=True))
        self.model.to(self.device)
        self.model.eval()

        self.transform = Compose([
            Resize((28, 28)),
            Grayscale(),
            ToTensor(),
        ])

    def predict(self, image: Path = Input(description="Image to classify")) -> dict:
        img = Image.open(image)
        input_tensor = self.transform(img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            pred = self.model(input_tensor)
            
        probs = pred[0].softmax(0)
        top3 = probs.topk(3)
        
        return {classes[i]: p.detach().item() for p, i in zip(*top3)}
