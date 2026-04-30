import torch
from torch import nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor
import optuna
import os

# Download data
training_data = datasets.FashionMNIST(
    root="data", train=True, download=True, transform=ToTensor(),
)
test_data = datasets.FashionMNIST(
    root="data", train=False, download=True, transform=ToTensor(),
)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {device} device")

# Define model builder
class OptimizedNeuralNetwork(nn.Module):
    def __init__(self, trial):
        super().__init__()
        self.flatten = nn.Flatten()
        
        # Hyperparameters to tune
        n_layers = trial.suggest_int("n_layers", 1, 3)
        layers = []
        in_features = 28 * 28
        
        for i in range(n_layers):
            out_features = trial.suggest_int(f"n_units_l{i}", 128, 512)
            layers.append(nn.Linear(in_features, out_features))
            layers.append(nn.ReLU())
            p = trial.suggest_float(f"dropout_l{i}", 0.2, 0.5)
            layers.append(nn.Dropout(p))
            in_features = out_features
            
        layers.append(nn.Linear(in_features, 10))
        self.linear_relu_stack = nn.Sequential(*layers)

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits

def objective(trial):
    model = OptimizedNeuralNetwork(trial).to(device)
    
    # Tune learning rate
    lr = trial.suggest_float("lr", 1e-4, 1e-1, log=True)
    
    # Tune optimizer
    optimizer_name = trial.suggest_categorical("optimizer", ["Adam", "SGD"])
    optimizer = getattr(optim, optimizer_name)(model.parameters(), lr=lr)
    
    loss_fn = nn.CrossEntropyLoss()
    
    # Tune batch size
    batch_size = trial.suggest_categorical("batch_size", [32, 64, 128])
    train_dataloader = DataLoader(training_data, batch_size=batch_size, shuffle=True)
    test_dataloader = DataLoader(test_data, batch_size=batch_size)
    
    # Train for a few epochs just to evaluate hyperparams
    epochs = 3
    for epoch in range(epochs):
        model.train()
        for batch, (X, y) in enumerate(train_dataloader):
            X, y = X.to(device), y.to(device)
            pred = model(X)
            loss = loss_fn(pred, y)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            
    # Evaluate
    model.eval()
    correct = 0
    with torch.no_grad():
        for X, y in test_dataloader:
            X, y = X.to(device), y.to(device)
            pred = model(X)
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
            
    accuracy = correct / len(test_dataloader.dataset)
    return accuracy

if __name__ == "__main__":
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=5) # 5 trials for speed
    
    print("Best trial:")
    trial = study.best_trial
    print("  Value: ", trial.value)
    print("  Params: ")
    for key, value in trial.params.items():
        print(f"    {key}: {value}")
        
    # Retrain best model
    print("Retraining best model on 15 epochs...")
    best_model = OptimizedNeuralNetwork(trial).to(device)
    
    lr = trial.params["lr"]
    optimizer_name = trial.params["optimizer"]
    optimizer = getattr(optim, optimizer_name)(best_model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()
    batch_size = trial.params["batch_size"]
    
    train_dataloader = DataLoader(training_data, batch_size=batch_size, shuffle=True)
    test_dataloader = DataLoader(test_data, batch_size=batch_size)
    
    epochs = 15
    for epoch in range(epochs):
        best_model.train()
        for X, y in train_dataloader:
            X, y = X.to(device), y.to(device)
            pred = best_model(X)
            loss = loss_fn(pred, y)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
        print(f"Epoch {epoch+1} done.")
            
    os.makedirs('optimized_model', exist_ok=True)
    # Save the architecture params so we can reconstruct it
    torch.save({
        'model_state_dict': best_model.state_dict(),
        'trial_params': trial.params
    }, "optimized_model/model.pth")
    print("Saved optimized model to optimized_model/model.pth")
