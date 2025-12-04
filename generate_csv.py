# build_csv.py
import os, csv
root = "dataset"
out_csv = "dataset.csv"
rows = []
try:
    for cls,label in [("healthy",0),("sick",1)]:
        d = os.path.join(root, cls)
        if not os.path.exists(d):
            print(f"Advertencia: El directorio {d} no existe")
            continue
        for fname in os.listdir(d):
            if fname.lower().endswith(('.jpg','.png','.jpeg')):
                rows.append([os.path.join(d,fname), label, "", cls])
    
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
