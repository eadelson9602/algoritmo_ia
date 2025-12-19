"""
Módulo para cargar el modelo entrenado y hacer predicciones sobre imágenes
"""
import os
import torch
import torch.nn as nn
import numpy as np
from PIL import Image, ImageOps
from pathlib import Path

# Configuración (debe coincidir con train_cats_pytorch.py)
IMG_SIZE = 128
MODEL_PATH = Path("artifacts/best_model.pth")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Arquitectura del modelo (debe coincidir con train_cats_pytorch.py)
class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        )
        feat = (IMG_SIZE // 8) * (IMG_SIZE // 8) * 128
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(feat, 256),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(256, 2)
        )

    def forward(self, x):
        return self.fc(self.conv(x))


def load_model():
    """Carga el modelo entrenado"""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Modelo no encontrado en {MODEL_PATH}. "
            "Primero debes entrenar el modelo ejecutando train_cats_pytorch.py"
        )
    
    model = SimpleCNN().to(device)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model.eval()
    return model


def preprocess_image(image_path: str):
    """
    Preprocesa una imagen para que sea compatible con el modelo
    
    Args:
        image_path: Ruta a la imagen
    
    Returns:
        Tensor preprocesado
    """
    # Cargar y convertir a RGB
    img = Image.open(image_path).convert('RGB')
    
    # Redimensionar
    img = img.resize((IMG_SIZE, IMG_SIZE))
    
    # Convertir a array y normalizar
    arr = np.array(img).astype('float32') / 255.0
    
    # Normalización con ImageNet stats (igual que en el entrenamiento)
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    arr = (arr - mean) / std
    
    # Transponer de HWC a CHW
    arr = np.transpose(arr, (2, 0, 1))
    
    # Convertir a tensor y agregar dimensión de batch
    tensor = torch.from_numpy(arr).float().unsqueeze(0)
    
    return tensor.to(device)


def predict_image(model, image_path: str):
    """
    Predice si una imagen es de un gato sano (healthy) o enfermo (sick)
    
    Args:
        model: Modelo cargado
        image_path: Ruta a la imagen
    
    Returns:
        dict con:
            - label: 0 para "healthy", 1 para "sick"
            - label_name: "healthy" o "sick"
            - confidence: confianza de la predicción (0-1)
            - probabilities: probabilidades para cada clase
    """
    # Preprocesar imagen
    tensor = preprocess_image(image_path)
    
    # Hacer predicción
    with torch.no_grad():
        output = model(tensor)
        probabilities = torch.softmax(output, dim=1)
        predicted_class = output.argmax(dim=1).item()
        confidence = probabilities[0][predicted_class].item()
    
    # Mapear a nombres
    label_names = {0: "healthy", 1: "sick"}
    label_names_es = {0: "sano", 1: "enfermo"}
    
    return {
        "label": predicted_class,
        "label_name": label_names[predicted_class],
        "label_name_es": label_names_es[predicted_class],
        "confidence": confidence,
        "probabilities": {
            "healthy": probabilities[0][0].item(),
            "sick": probabilities[0][1].item()
        }
    }


# Modelo global (se carga una vez al importar)
_model = None

def get_model():
    """Obtiene el modelo (lo carga si es necesario)"""
    global _model
    if _model is None:
        _model = load_model()
    return _model
