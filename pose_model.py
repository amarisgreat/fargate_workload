import io
import torch
import torchvision.transforms as transforms
from PIL import Image

# Load the model (CPU only)
model = torch.jit.load("model/pose_classifier_model_conv.pt", map_location=torch.device("cpu"))
model.eval()

# Label mapping
label_mapping = {
    2: "Droopy Necks",
    1: "Healthy",
    0: "Slipped Tendon"
}

# Image preprocessing function
def transform_image(image_bytes):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return transform(image).unsqueeze(0).to(torch.device("cpu"))

# Prediction function
def predict(image_bytes):
    input_tensor = transform_image(image_bytes)

    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.nn.functional.softmax(output, dim=1)[0]
        predicted_class = torch.argmax(probabilities).item()
        confidence = probabilities[predicted_class].item()

    predicted_label = label_mapping.get(predicted_class, "Unknown")
    
    return {
        "class": predicted_label,
        "probability": round(confidence * 100, 2),
        "all_probabilities": {label_mapping[i]: round(probabilities[i].item() * 100, 2) for i in range(len(label_mapping))}
    }
