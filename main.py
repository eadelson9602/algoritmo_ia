"""
Backend API para procesamiento de imágenes con IA
FastAPI - Servicio web para procesar imágenes y generar CSV
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import List
import os
import tempfile
import shutil
import uuid
from pathlib import Path
import uvicorn
from PIL import Image
from datetime import datetime

# Importar pandas al inicio para asegurar que esté disponible
import sys
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
    print(f"✅ pandas cargado al inicio desde: {pd.__file__}")
except ImportError as e:
    PANDAS_AVAILABLE = False
    print(f"❌ ERROR CRÍTICO: pandas no está instalado")
    print(f"   Python usado: {sys.executable}")
    print(f"   Instala con: {sys.executable} -m pip install pandas")
    print(f"   Error: {e}")

# Importar módulo de predicción
try:
    from predict import get_model, predict_image
    MODEL_AVAILABLE = True
except ImportError:
    MODEL_AVAILABLE = False
    print("⚠️  Advertencia: No se pudo importar el módulo de predicción. "
          "Las imágenes se procesarán sin clasificación.")
except Exception as e:
    MODEL_AVAILABLE = False
    print(f"⚠️  Advertencia: Error al cargar el modelo: {e}")

app = FastAPI(
    title="Image Processor API",
    description="API para procesar imágenes con IA y generar CSV",
    version="1.0.0"
)

# Configurar CORS para permitir requests del frontend
import os
allowed_origins = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3001,*"
).split(",")
# Limpiar espacios y filtrar "*" si hay otros orígenes
allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if "*" not in allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directorio para almacenar archivos temporales
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Image Processor API está funcionando", "status": "ok"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/api/v1/images/process")
async def process_images(
    files: List[UploadFile] = File(...),
    options: dict = None
):
    """
    Procesa múltiples imágenes y genera un CSV con los resultados
    
    Args:
        files: Lista de archivos de imagen a procesar
        options: Opciones adicionales para el procesamiento
    
    Returns:
        JSON con información del procesamiento y URL para descargar el CSV
    """
    if not files:
        raise HTTPException(status_code=400, detail="No se proporcionaron archivos")
    
    # Validar tipos de archivo - soporta todos los formatos que Pillow puede leer
    # No limitamos por extensión, validamos intentando abrir la imagen con Pillow
    processed_files = []
    errors = []
    
    def is_valid_image_file(filepath):
        """Verifica que el archivo sea una imagen válida que Pillow pueda procesar"""
        try:
            with Image.open(filepath) as img:
                # Verificar que sea una imagen válida
                img.verify()
            # Intentar abrir y convertir a RGB para asegurar compatibilidad con el modelo
            with Image.open(filepath) as img:
                img.convert('RGB')  # Esto asegura que podemos procesarla
            return True
        except Exception:
            return False
    
    try:
        # Guardar archivos temporalmente
        temp_files = []
        for file in files:
            # Guardar archivo temporal primero para validarlo
            # Usamos un nombre único para evitar conflictos
            file_ext = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            temp_path = UPLOAD_DIR / unique_filename
            
            # Guardar el archivo
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Validar que realmente sea una imagen válida
            if not is_valid_image_file(temp_path):
                errors.append(f"Archivo {file.filename}: no es una imagen válida o formato no soportado")
                if temp_path.exists():
                    temp_path.unlink()  # Eliminar archivo inválido
                continue
            
            temp_files.append(temp_path)
            
            # Clasificar con IA si el modelo está disponible
            classification = None
            if MODEL_AVAILABLE:
                try:
                    model = get_model()
                    prediction = predict_image(model, str(temp_path))
                    classification = {
                        "label": prediction["label"],
                        "label_name": prediction["label_name"],
                        "label_name_es": prediction["label_name_es"],
                        "confidence": round(prediction["confidence"], 4)
                    }
                    
                    # Guardar feedback automáticamente para aprendizaje continuo
                    try:
                        from feedback_storage import save_feedback
                        save_feedback(
                            image_path=str(temp_path),
                            predicted_label=prediction["label"],
                            predicted_label_name=prediction["label_name"],
                            confidence=prediction["confidence"]
                        )
                    except ImportError as e:
                        print(f"⚠️  No se pudo importar feedback_storage (pandas no disponible): {e}")
                    except Exception as e:
                        print(f"⚠️  No se pudo guardar feedback para {file.filename}: {e}")
                        
                except Exception as e:
                    print(f"Error al clasificar {file.filename}: {e}")
                    classification = {"error": str(e)}
            
            processed_files.append({
                "filename": file.filename,  # Nombre original del archivo
                "path": str(temp_path),      # Ruta donde se guardó
                "size": temp_path.stat().st_size,
                "status": "processed",
                "classification": classification
            })
        
        # Generar CSV usando la función de generate_csv.py
        csv_path = await generate_csv(processed_files, options)
        
        # Obtener estadísticas actualizadas después de procesar
        total_images_after = 0
        try:
            from feedback_storage import get_statistics
            stats = get_statistics()
            total_images_after = stats['total_images']
        except:
            pass
        
        return JSONResponse({
            "success": True,
            "message": f"Se procesaron {len(processed_files)} imágenes",
            "processed_files": [
                {
                    "filename": f["filename"],
                    "size": f["size"],
                    "status": f["status"],
                    "classification": f.get("classification"),
                    "path": f.get("path")  # Incluir ruta para correcciones
                }
                for f in processed_files
            ],
            "errors": errors if errors else None,
            "csv_url": f"/api/v1/files/download/{Path(csv_path).name}",
            "csv_filename": Path(csv_path).name,
            "total_images_processed": total_images_after  # Incluir total para trigger automático
        })
    
    except Exception as e:
        # Limpiar archivos temporales en caso de error
        for temp_file in temp_files:
            if temp_file.exists():
                temp_file.unlink()
        
        raise HTTPException(status_code=500, detail=f"Error procesando imágenes: {str(e)}")


@app.get("/api/v1/files/download/{filename}")
async def download_file(filename: str):
    """
    Descarga un archivo generado (CSV, etc.)
    
    Args:
        filename: Nombre del archivo a descargar
    
    Returns:
        Archivo para descarga
    """
    file_path = OUTPUT_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="text/csv"
    )


async def generate_csv(processed_files: List[dict], options: dict = None) -> str:
    """
    Genera un archivo CSV con los resultados del procesamiento
    Adapta la lógica de generate_csv.py para trabajar con archivos subidos
    
    Args:
        processed_files: Lista de archivos procesados con sus rutas
        options: Opciones adicionales
    
    Returns:
        Ruta del archivo CSV generado
    """
    import csv
    from datetime import datetime
    
    # Generar nombre único para el CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"processed_images_{timestamp}.csv"
    csv_path = OUTPUT_DIR / csv_filename
    
    # Escribir CSV siguiendo el formato de generate_csv.py
    # Formato: image_path, label, timestamp, source, label_name
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["image_path", "label", "timestamp", "source", "label_name"])
        
        for file_info in processed_files:
            # Usar la clasificación del modelo si está disponible
            classification = file_info.get("classification")
            if classification and "error" not in classification:
                label = classification["label"]  # 0 para healthy, 1 para sick
                label_name = classification["label_name_es"]  # "sano" o "enfermo"
            else:
                label = ""
                label_name = "no clasificado"
            
            timestamp_str = datetime.now().isoformat()
            source = "api_upload"
            
            writer.writerow([
                file_info["path"],
                label,
                timestamp_str,
                source,
                label_name  # Agregar nombre de la clase en español
            ])
    
    return str(csv_path)


@app.delete("/api/v1/files/{filename}")
async def delete_file(filename: str):
    """
    Elimina un archivo generado
    
    Args:
        filename: Nombre del archivo a eliminar
    """
    file_path = OUTPUT_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    file_path.unlink()
    return {"message": f"Archivo {filename} eliminado correctamente"}


from pydantic import BaseModel

class CorrectionRequest(BaseModel):
    image_path: str
    corrected_label: int
    corrected_label_name: str = None
    user_feedback: str = None

@app.post("/api/v1/feedback/correct")
async def correct_classification(correction: CorrectionRequest):
    """
    Permite corregir una clasificación para mejorar el modelo
    
    Args:
        correction: Objeto con image_path, corrected_label, etc.
    """
    try:
        from feedback_storage import save_feedback, get_feedback_data
        
        # Buscar la predicción original en el feedback
        df = get_feedback_data()
        if df.empty:
            raise HTTPException(status_code=404, detail="No se encontró la imagen en el historial")
        
        # Buscar por image_path
        matching = df[df['image_path'] == correction.image_path]
        if matching.empty:
            raise HTTPException(status_code=404, detail="Imagen no encontrada en el historial")
        
        # Obtener la última entrada para esta imagen
        last_entry = matching.iloc[-1]
        
        # Guardar corrección
        label_names = {0: "healthy", 1: "sick"}
        label_names_es = {0: "sano", 1: "enfermo"}
        
        save_feedback(
            image_path=correction.image_path,
            predicted_label=int(last_entry['predicted_label']),
            predicted_label_name=last_entry['predicted_label_name'],
            confidence=float(last_entry['confidence']),
            corrected_label=correction.corrected_label,
            corrected_label_name=correction.corrected_label_name or label_names_es.get(correction.corrected_label, ""),
            user_feedback=correction.user_feedback
        )
        
        return {
            "success": True,
            "message": "Corrección guardada. El modelo se reentrenará con estos datos."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando corrección: {str(e)}")


@app.get("/api/v1/feedback/stats")
async def get_feedback_stats():
    """Obtiene estadísticas del feedback para aprendizaje continuo"""
    try:
        # Verificar que pandas esté disponible
        if not PANDAS_AVAILABLE:
            return {
                "total_images": 0,
                "corrections": 0,
                "accuracy_estimate": 0.0,
                "error": "pandas no está disponible. Instala con: pip install pandas"
            }
        
        from feedback_storage import get_statistics
        stats = get_statistics()
        # Asegurar que siempre retornamos un diccionario válido
        if not isinstance(stats, dict):
            stats = {
                "total_images": 0,
                "corrections": 0,
                "accuracy_estimate": 0.0
            }
        return stats
    except ImportError as e:
        import sys
        error_msg = f"Error importando feedback_storage. Python: {sys.executable}, Error: {str(e)}"
        print(f"⚠️  {error_msg}")
        return {
            "total_images": 0,
            "corrections": 0,
            "accuracy_estimate": 0.0,
            "error": error_msg
        }
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"⚠️  Error en get_feedback_stats: {error_detail}")
        # Retornar valores por defecto en lugar de lanzar error
        return {
            "total_images": 0,
            "corrections": 0,
            "accuracy_estimate": 0.0,
            "error": str(e)
        }


# Estado global del reentrenamiento
retraining_state = {
    "status": "idle",  # idle, running, completed, error
    "progress": 0,
    "message": "",
    "error": None,
    "started_at": None,
    "completed_at": None
}

import threading

def run_retraining_background(epochs: int, min_feedback: int):
    """Ejecuta el reentrenamiento en background"""
    global retraining_state
    try:
        retraining_state["status"] = "running"
        retraining_state["progress"] = 0
        retraining_state["message"] = "Iniciando reentrenamiento..."
        retraining_state["error"] = None
        retraining_state["started_at"] = datetime.now().isoformat()
        retraining_state["completed_at"] = None
        
        import subprocess
        from feedback_storage import get_statistics
        
        stats = get_statistics()
        if stats['total_images'] < min_feedback:
            retraining_state["status"] = "error"
            retraining_state["message"] = f"Se requieren al menos {min_feedback} imágenes de feedback"
            retraining_state["error"] = f"Actualmente hay {stats['total_images']} imágenes"
            return
        
        retraining_state["progress"] = 10
        retraining_state["message"] = "Ejecutando script de reentrenamiento..."
        
        # Ejecutar reentrenamiento
        result = subprocess.run(
            ["python", "incremental_train.py", "--epochs", str(epochs), "--min-feedback", str(min_feedback)],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hora máximo
        )
        
        if result.returncode == 0:
            retraining_state["status"] = "completed"
            retraining_state["progress"] = 100
            retraining_state["message"] = "Reentrenamiento completado exitosamente"
            retraining_state["completed_at"] = datetime.now().isoformat()
        else:
            retraining_state["status"] = "error"
            retraining_state["message"] = "Error durante el reentrenamiento"
            retraining_state["error"] = result.stderr[:500]  # Limitar tamaño del error
            retraining_state["completed_at"] = datetime.now().isoformat()
            
    except subprocess.TimeoutExpired:
        retraining_state["status"] = "error"
        retraining_state["message"] = "El reentrenamiento excedió el tiempo límite"
        retraining_state["error"] = "Timeout después de 1 hora"
        retraining_state["completed_at"] = datetime.now().isoformat()
    except Exception as e:
        retraining_state["status"] = "error"
        retraining_state["message"] = f"Error ejecutando reentrenamiento: {str(e)}"
        retraining_state["error"] = str(e)
        retraining_state["completed_at"] = datetime.now().isoformat()

@app.post("/api/v1/model/retrain")
async def trigger_retraining(epochs: int = 10, min_feedback: int = 10):
    """
    Dispara el reentrenamiento incremental del modelo (en background)
    
    Args:
        epochs: Número de épocas para reentrenar (default: 10)
        min_feedback: Mínimo de imágenes de feedback requeridas (default: 10)
    
    Returns:
        Estado del reentrenamiento iniciado
    """
    global retraining_state
    
    # Si ya hay un reentrenamiento en curso, no iniciar otro
    if retraining_state["status"] == "running":
        return {
            "success": False,
            "message": "Ya hay un reentrenamiento en curso",
            "state": retraining_state
        }
    
    from feedback_storage import get_statistics
    stats = get_statistics()
    
    if stats['total_images'] < min_feedback:
        return {
            "success": False,
            "message": f"Se requieren al menos {min_feedback} imágenes de feedback. Actualmente hay {stats['total_images']}",
            "stats": stats
        }
    
    # Iniciar reentrenamiento en background
    thread = threading.Thread(
        target=run_retraining_background,
        args=(epochs, min_feedback),
        daemon=True
    )
    thread.start()
    
    return {
        "success": True,
        "message": "Reentrenamiento iniciado en background",
        "state": retraining_state
    }

@app.get("/api/v1/model/retrain/status")
async def get_retraining_status():
    """
    Obtiene el estado actual del reentrenamiento
    
    Returns:
        Estado del reentrenamiento (idle, running, completed, error)
    """
    global retraining_state
    return retraining_state


if __name__ == "__main__":
    import os
    import sys
    
    # Verificar que pandas esté disponible antes de iniciar
    if not PANDAS_AVAILABLE:
        print("⚠️  ERROR: pandas no está disponible. El servidor no puede iniciar correctamente.")
        print(f"   Python usado: {sys.executable}")
        print("   Instala pandas con: python -m pip install pandas")
        sys.exit(1)
    
    port = int(os.environ.get("PORT", 8000))
    print(f"✅ Iniciando servidor en puerto {port}")
    print(f"   Python: {sys.executable}")
    print(f"   Pandas disponible: {PANDAS_AVAILABLE}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
