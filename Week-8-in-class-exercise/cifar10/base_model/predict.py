import torch
from torch import nn
from cog import BasePredictor, Input, Path
from PIL import Image
from torchvision.transforms import ToTensor, Resize, Compose

class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(3*32*32, 512),
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
    "airplane", "automobile", "bird", "cat", "deer", 
    "dog", "frog", "horse", "ship", "truck"
]

class Predictor(BasePredictor):
    def setup(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = NeuralNetwork()
        self.model.load_state_dict(torch.load("model.pth", map_location=self.device, weights_only=True))
        self.model.to(self.device)
        self.model.eval()

        self.transform = Compose([
            Resize((32, 32)),
            ToTensor(),
        ])

    def predict(self, image: Path = Input(description="Image to classify")) -> dict:
        img = Image.open(image).convert("RGB")
        input_tensor = self.transform(img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            pred = self.model(input_tensor)
            
        probs = pred[0].softmax(0)
        top3 = probs.topk(3)
        
        return {classes[i]: p.detach().item() for p, i in zip(*top3)}
