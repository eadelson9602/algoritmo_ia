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
        
        return JSONResponse({
            "success": True,
            "message": f"Se procesaron {len(processed_files)} imágenes",
            "processed_files": [
                {
                    "filename": f["filename"],
                    "size": f["size"],
                    "status": f["status"],
                    "classification": f.get("classification")
                }
                for f in processed_files
            ],
            "errors": errors if errors else None,
            "csv_url": f"/api/v1/files/download/{Path(csv_path).name}",
            "csv_filename": Path(csv_path).name
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


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
