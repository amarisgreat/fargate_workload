import io
import os
import torch
import torch.nn as nn
from efficientnet_pytorch import EfficientNet
from PIL import Image
from torchvision import transforms

# Use CPU for compatibility on hosting platforms
device = torch.device('cpu')

# Dynamically resolve the path to the model file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'model', 'litter_classifier_model.pth')

# Load model architecture and weights
num_classes = 4
model = EfficientNet.from_name('efficientnet-b3')
model._fc = nn.Linear(model._fc.in_features, num_classes)

# Load weights to model
model.load_state_dict(torch.load(model_path, map_location=device))
model.to(device)
model.eval()

# Class labels
class_labels = ["Healthy", "Coccidiosis", "Salmonella", "Newcastle"]

# Image preprocessing
def transform_image(image_bytes):
    transform = transforms.Compose([
        transforms.Resize((300, 300)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                             std=[0.229, 0.224, 0.225]),
    ])
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    return transform(image).unsqueeze(0).to(device)

# Predict litter class
def predict_litter(image_bytes):
    input_tensor = transform_image(image_bytes)
    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.nn.functional.softmax(output, dim=1)[0]
        predicted_class = torch.argmax(probabilities).item()
        confidence = probabilities[predicted_class].item()

    return {
        "class": class_labels[predicted_class],
        "probability": round(confidence * 100, 2),
        "all_probabilities": {
            class_labels[i]: round(probabilities[i].item() * 100, 2)
            for i in range(num_classes)
        }
    }
