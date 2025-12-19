# build_csv.py
import os, csv
from PIL import Image

root = "dataset"
out_csv = "dataset.csv"
rows = []

def is_valid_image(filepath):
    """Verifica que el archivo sea una imagen válida intentando abrirla con Pillow"""
    try:
        with Image.open(filepath) as img:
            # Verificar que sea una imagen válida
            img.verify()
        # Intentar abrir y convertir a RGB para asegurar compatibilidad
        with Image.open(filepath) as img:
            img.convert('RGB')  # Esto asegura que podemos procesarla
        return True
    except Exception:
        return False

try:
    for cls,label in [("healthy",0),("sick",1)]:
        d = os.path.join(root, cls)
        if not os.path.exists(d):
            print(f"Advertencia: El directorio {d} no existe")
            continue
        for fname in os.listdir(d):
            filepath = os.path.join(d, fname)
            # Verificar que sea un archivo (no directorio)
            if os.path.isfile(filepath):
                # Intentar validar como imagen (no importa la extensión)
                if is_valid_image(filepath):
                    rows.append([os.path.join(d,fname), label, "", cls])
                else:
                    # Solo mostrar advertencia si tiene extensión de imagen común
                    ext = os.path.splitext(fname)[1].lower()
                    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif']:
                        print(f"Advertencia: {fname} no es una imagen válida, se omite")
    
    with open(out_csv,'w',newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['image_path','label','timestamp','source'])
        writer.writerows(rows)
    print(f"CSV creado exitosamente: {out_csv}")
    print(f"Total de imágenes procesadas: {len(rows)}")
except Exception as e:
    print(f"Error al crear el CSV: {e}")
    import traceback
    traceback.print_exc()
