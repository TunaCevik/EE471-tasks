import torch
from torch import nn
from cog import BasePredictor, Input, Path
from PIL import Image
from torchvision.transforms import ToTensor, Resize, Compose

class OptimizedNeuralNetwork(nn.Module):
    def __init__(self, trial_params):
        super().__init__()
        
        out_channels_1 = trial_params["out_channels_1"]
        out_channels_2 = trial_params["out_channels_2"]
        
        self.conv1 = nn.Conv2d(3, out_channels_1, kernel_size=3, padding=1)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(2)
        
        self.conv2 = nn.Conv2d(out_channels_1, out_channels_2, kernel_size=3, padding=1)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(2)
        
        self.flatten = nn.Flatten()
        
        in_features = out_channels_2 * 8 * 8
        linear_units = trial_params["linear_units"]
        
        self.fc1 = nn.Linear(in_features, linear_units)
        self.relu3 = nn.ReLU()
        p = trial_params["dropout"]
        self.dropout = nn.Dropout(p)
        self.fc2 = nn.Linear(linear_units, 10)

    def forward(self, x):
        x = self.pool1(self.relu1(self.conv1(x)))
        x = self.pool2(self.relu2(self.conv2(x)))
        x = self.flatten(x)
        x = self.dropout(self.relu3(self.fc1(x)))
        x = self.fc2(x)
        return x

classes = [
    "airplane", "automobile", "bird", "cat", "deer", 
    "dog", "frog", "horse", "ship", "truck"
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
