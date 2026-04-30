import torch
from torch import nn
from cog import BasePredictor, Input, Path
from PIL import Image
from torchvision.transforms import ToTensor, Resize, Grayscale, Compose

# Define model builder using same architecture logic as in train_optimized.py
class OptimizedNeuralNetwork(nn.Module):
    def __init__(self, trial_params):
        super().__init__()
        self.flatten = nn.Flatten()
        
        n_layers = trial_params["n_layers"]
        layers = []
        in_features = 28 * 28
        
        for i in range(n_layers):
            out_features = trial_params[f"n_units_l{i}"]
            layers.append(nn.Linear(in_features, out_features))
            layers.append(nn.ReLU())
            p = trial_params[f"dropout_l{i}"]
            layers.append(nn.Dropout(p))
            in_features = out_features
            
        layers.append(nn.Linear(in_features, 10))
        self.linear_relu_stack = nn.Sequential(*layers)

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
        
        checkpoint = torch.load("model.pth", map_location=self.device, weights_only=True)
        trial_params = checkpoint['trial_params']
        
        self.model = OptimizedNeuralNetwork(trial_params)
        self.model.load_state_dict(checkpoint['model_state_dict'])
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
