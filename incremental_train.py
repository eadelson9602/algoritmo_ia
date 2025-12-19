"""
Script para reentrenamiento incremental del modelo con nuevos datos
Este script se puede ejecutar periódicamente para mejorar el modelo con feedback de usuarios
"""
import os
import sys
import pandas as pd
from pathlib import Path
from feedback_storage import get_training_data, copy_image_to_training, get_statistics
# Importar SimpleCNN y CatsDataset desde train_cats_pytorch
# Usamos import directo ya que están en el mismo directorio
from train_cats_pytorch import SimpleCNN
import train_cats_pytorch as train_module
CatsDataset = train_module.CatsDataset
IMG_SIZE = train_module.IMG_SIZE
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, ConcatDataset
import shutil

# Configuración
ORIGINAL_DATASET = "dataset.csv"
FEEDBACK_DATASET = "feedback_data/feedback.csv"
ARTIFACTS_DIR = Path("artifacts")
BACKUP_DIR = Path("artifacts/backups")
BACKUP_DIR.mkdir(exist_ok=True)

def load_original_dataset():
    """Carga el dataset original si existe"""
    if os.path.exists(ORIGINAL_DATASET):
        return pd.read_csv(ORIGINAL_DATASET)
    return pd.DataFrame()

def prepare_incremental_dataset():
    """
    Prepara un dataset combinado con datos originales y feedback
    """
    # Cargar dataset original
    original_df = load_original_dataset()
    
    # Cargar datos de feedback
    feedback_df = get_training_data()
    
    if feedback_df.empty:
        print("⚠️  No hay datos de feedback para reentrenar")
        return None
    
    # Copiar imágenes de feedback al directorio de entrenamiento organizado
    print(f"📦 Copiando {len(feedback_df)} imágenes de feedback al dataset...")
    new_paths = []
    for idx, row in feedback_df.iterrows():
        if os.path.exists(row['image_path']):
            new_path = copy_image_to_training(row['image_path'], int(row['label']))
            new_paths.append(new_path)
        else:
            print(f"⚠️  Imagen no encontrada: {row['image_path']}")
    
    # Crear nuevo CSV combinado
    combined_df = pd.DataFrame({
        'image_path': new_paths,
        'label': feedback_df['label'].values,
        'timestamp': feedback_df['timestamp'].values,
        'source': ['feedback'] * len(feedback_df)
    })
    
    # Agregar datos originales si existen
    if not original_df.empty:
        original_df['source'] = 'original'
        combined_df = pd.concat([original_df, combined_df], ignore_index=True)
    
    # Guardar CSV combinado
    combined_csv = "dataset_incremental.csv"
    combined_df.to_csv(combined_csv, index=False)
    print(f"✅ Dataset combinado guardado en {combined_csv}")
    print(f"   - Imágenes originales: {len(original_df) if not original_df.empty else 0}")
    print(f"   - Imágenes de feedback: {len(feedback_df)}")
    print(f"   - Total: {len(combined_df)}")
    
    return combined_csv

def backup_current_model():
    """Hace backup del modelo actual antes de reentrenar"""
    model_path = ARTIFACTS_DIR / "best_model.pth"
    if model_path.exists():
        from datetime import datetime
        backup_name = f"best_model_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pth"
        backup_path = BACKUP_DIR / backup_name
        shutil.copy2(model_path, backup_path)
        print(f"💾 Backup del modelo guardado en {backup_path}")
        return backup_path
    return None

def retrain_model(incremental_csv: str, epochs: int = 10):
    """
    Reentrena el modelo con el dataset incremental
    
    Args:
        incremental_csv: Ruta al CSV con datos combinados
        epochs: Número de épocas para reentrenar
    """
    print(f"\n🔄 Iniciando reentrenamiento incremental...")
    print(f"   CSV: {incremental_csv}")
    print(f"   Épocas: {epochs}")
    
    # Hacer backup del modelo actual
    backup_path = backup_current_model()
    
    try:
        # Modificar train_cats_pytorch.py para usar el CSV incremental
        # Por ahora, vamos a crear una versión simplificada aquí
        
        import train_cats_pytorch as train_module
        
        # Cargar el modelo actual
        model_path = ARTIFACTS_DIR / "best_model.pth"
        if not model_path.exists():
            print("❌ No se encontró el modelo actual. Entrenando desde cero...")
            # Ejecutar entrenamiento normal
            os.system(f"python train_cats_pytorch.py")
            return
        
        # Cargar modelo existente
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = SimpleCNN().to(device)
        model.load_state_dict(torch.load(model_path, map_location=device))
        print(f"✅ Modelo actual cargado desde {model_path}")
        
        # Cargar datos incrementales
        df = pd.read_csv(incremental_csv)
        print(f"📊 Dataset: {len(df)} imágenes")
        
        # Dividir en train/val/test
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        n = len(df)
        train_df = df.iloc[:int(0.7*n)]
        val_df = df.iloc[int(0.7*n):int(0.85*n)]
        test_df = df.iloc[int(0.85*n):]
        
        print(f"   Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
        
        # Crear datasets
        train_dataset = CatsDataset(train_df, train=True)
        val_dataset = CatsDataset(val_df, train=False)
        test_dataset = CatsDataset(test_df, train=False)
        
        train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
        test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)
        
        # Reentrenar (fine-tuning)
        import torch.optim as optim
        optimizer = optim.Adam(model.parameters(), lr=0.0001, weight_decay=1e-4)  # Learning rate más bajo para fine-tuning
        criterion = nn.CrossEntropyLoss()
        
        best_val_acc = 0.0
        
        for epoch in range(epochs):
            # Training
            model.train()
            train_loss = 0.0
            train_correct = 0
            train_total = 0
            for images, labels in train_loader:
                images, labels = images.to(device), labels.to(device)
                optimizer.zero_grad()
                outputs = model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                train_total += labels.size(0)
                train_correct += (predicted == labels).sum().item()
            
            train_acc = train_correct / train_total if train_total > 0 else 0.0
            
            # Validation
            model.eval()
            val_correct = 0
            val_total = 0
            val_loss = 0.0
            with torch.no_grad():
                for images, labels in val_loader:
                    images, labels = images.to(device), labels.to(device)
                    outputs = model(images)
                    loss = criterion(outputs, labels)
                    val_loss += loss.item()
                    _, predicted = torch.max(outputs.data, 1)
                    val_total += labels.size(0)
                    val_correct += (predicted == labels).sum().item()
            
            val_acc = val_correct / val_total if val_total > 0 else 0.0
            avg_train_loss = train_loss / len(train_loader) if len(train_loader) > 0 else 0.0
            avg_val_loss = val_loss / len(val_loader) if len(val_loader) > 0 else 0.0
            
            print(f"Epoch {epoch+1}/{epochs} - Train Loss: {avg_train_loss:.4f}, Train Acc: {train_acc:.4f}, Val Loss: {avg_val_loss:.4f}, Val Acc: {val_acc:.4f}")
            
            # Guardar mejor modelo
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save(model.state_dict(), model_path)
                print(f"   ✅ Nuevo mejor modelo guardado (Val Acc: {val_acc:.4f})")
        
        # Test final
        model.eval()
        test_correct = 0
        test_total = 0
        with torch.no_grad():
            for images, labels in test_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, predicted = torch.max(outputs.data, 1)
                test_total += labels.size(0)
                test_correct += (predicted == labels).sum().item()
        
        test_acc = test_correct / test_total
        print(f"\n✅ Reentrenamiento completado!")
        print(f"   Precisión en test: {test_acc:.4f}")
        print(f"   Modelo guardado en: {model_path}")
        
    except Exception as e:
        print(f"❌ Error durante el reentrenamiento: {e}")
        import traceback
        traceback.print_exc()
        
        # Restaurar backup si hay error
        if backup_path and backup_path.exists():
            print(f"🔄 Restaurando modelo desde backup...")
            shutil.copy2(backup_path, model_path)
            print(f"✅ Modelo restaurado")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Reentrenamiento incremental del modelo")
    parser.add_argument("--epochs", type=int, default=10, help="Número de épocas")
    parser.add_argument("--min-feedback", type=int, default=10, help="Mínimo de imágenes de feedback requeridas")
    
    args = parser.parse_args()
    
    # Verificar estadísticas
    stats = get_statistics()
    print(f"📊 Estadísticas de feedback:")
    print(f"   - Total de imágenes: {stats['total_images']}")
    print(f"   - Correcciones: {stats['corrections']}")
    print(f"   - Precisión estimada: {stats['accuracy_estimate']:.4f}")
    
    if stats['total_images'] < args.min_feedback:
        print(f"\n⚠️  Se requieren al menos {args.min_feedback} imágenes de feedback para reentrenar")
        print(f"   Actualmente hay: {stats['total_images']}")
        sys.exit(0)
    
    # Preparar dataset incremental
    incremental_csv = prepare_incremental_dataset()
    
    if incremental_csv:
        # Reentrenar
        retrain_model(incremental_csv, epochs=args.epochs)
    else:
        print("❌ No se pudo preparar el dataset incremental")
        sys.exit(1)
