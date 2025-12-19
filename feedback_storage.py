"""
Sistema de almacenamiento de feedback y datos para reentrenamiento
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Importar pandas - crítico para el funcionamiento
import sys
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError as e:
    PANDAS_AVAILABLE = False
    error_msg = f"pandas no está instalado en {sys.executable}. Instala con: {sys.executable} -m pip install pandas"
    print(f"❌ ERROR CRÍTICO: {error_msg}")
    print(f"   Error: {e}")
    raise ImportError(error_msg)

FEEDBACK_DIR = Path("feedback_data")
FEEDBACK_CSV = FEEDBACK_DIR / "feedback.csv"
IMAGES_DIR = FEEDBACK_DIR / "images"

# Crear directorios si no existen
FEEDBACK_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

def save_feedback(
    image_path: str,
    predicted_label: int,
    predicted_label_name: str,
    confidence: float,
    corrected_label: Optional[int] = None,
    corrected_label_name: Optional[str] = None,
    user_feedback: Optional[str] = None
) -> Dict:
    """
    Guarda feedback de una imagen procesada
    
    Args:
        image_path: Ruta original de la imagen
        predicted_label: Label predicho por el modelo (0 o 1)
        predicted_label_name: Nombre del label predicho
        confidence: Confianza de la predicción
        corrected_label: Label corregido por el usuario (opcional)
        corrected_label_name: Nombre del label corregido (opcional)
        user_feedback: Comentario del usuario (opcional)
    
    Returns:
        Dict con información del feedback guardado
    """
    feedback_data = {
        "timestamp": datetime.now().isoformat(),
        "image_path": str(image_path),
        "predicted_label": predicted_label,
        "predicted_label_name": predicted_label_name,
        "confidence": confidence,
        "corrected_label": corrected_label,
        "corrected_label_name": corrected_label_name,
        "user_feedback": user_feedback,
        "needs_review": corrected_label is not None
    }
    
    # Guardar en CSV
    df = pd.DataFrame([feedback_data])
    
    if FEEDBACK_CSV.exists():
        existing_df = pd.read_csv(FEEDBACK_CSV)
        df = pd.concat([existing_df, df], ignore_index=True)
    
    df.to_csv(FEEDBACK_CSV, index=False)
    
    return feedback_data

def get_feedback_data() -> pd.DataFrame:
    """Obtiene todos los datos de feedback"""
    if FEEDBACK_CSV.exists():
        try:
            df = pd.read_csv(FEEDBACK_CSV)
            # Verificar que el DataFrame no esté vacío y tenga las columnas necesarias
            if df.empty:
                return pd.DataFrame()
            return df
        except Exception as e:
            print(f"⚠️  Error leyendo feedback.csv: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def get_training_data() -> pd.DataFrame:
    """
    Obtiene datos listos para entrenamiento:
    - Usa labels corregidos si existen
    - Usa labels predichos si no hay corrección
    """
    df = get_feedback_data()
    
    if df.empty:
        return pd.DataFrame()
    
    # Crear columna 'label' que use corrección si existe, sino predicción
    df['label'] = df.apply(
        lambda row: row['corrected_label'] if pd.notna(row['corrected_label']) else row['predicted_label'],
        axis=1
    )
    
    # Filtrar solo las que tienen imagen válida
    df = df[df['image_path'].notna()]
    
    return df[['image_path', 'label', 'timestamp']].copy()

def copy_image_to_training(image_path: str, label: int) -> str:
    """
    Copia una imagen al directorio de entrenamiento organizado por label
    
    Args:
        image_path: Ruta de la imagen original
        label: Label (0=healthy, 1=sick)
    
    Returns:
        Nueva ruta de la imagen en el directorio de entrenamiento
    """
    import uuid
    import shutil
    
    label_dir = IMAGES_DIR / ("healthy" if label == 0 else "sick")
    label_dir.mkdir(exist_ok=True)
    
    # Generar nombre único
    original_path = Path(image_path)
    new_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{original_path.suffix}"
    new_path = label_dir / new_filename
    
    # Copiar imagen
    shutil.copy2(image_path, new_path)
    
    return str(new_path)

def get_statistics() -> Dict:
    """Obtiene estadísticas del feedback"""
    try:
        df = get_feedback_data()
        
        if df.empty:
            return {
                "total_images": 0,
                "corrections": 0,
                "accuracy_estimate": 0.0
            }
        
        total = len(df)
        
        # Verificar que la columna 'needs_review' existe antes de usarla
        if 'needs_review' in df.columns:
            corrections = df['needs_review'].sum()
        else:
            # Si no existe la columna, contar las que tienen corrected_label
            corrections = df['corrected_label'].notna().sum() if 'corrected_label' in df.columns else 0
        
        # Estimar precisión basada en correcciones
        accuracy = 1.0 - (corrections / total) if total > 0 else 0.0
        
        return {
            "total_images": total,
            "corrections": int(corrections),
            "accuracy_estimate": round(accuracy, 4)
        }
    except Exception as e:
        print(f"⚠️  Error obteniendo estadísticas: {e}")
        # Retornar valores por defecto en caso de error
        return {
            "total_images": 0,
            "corrections": 0,
            "accuracy_estimate": 0.0
        }
