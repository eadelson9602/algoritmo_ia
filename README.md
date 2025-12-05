# 🐱 Clasificación de Gatos: Healthy vs Sick

Este proyecto implementa un modelo de clasificación de imágenes usando PyTorch para distinguir entre gatos sanos y enfermos.

## 📋 Tabla de Contenidos

- [Requisitos](#requisitos)
- [Instalación de Paquetes](#instalación-de-paquetes)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Orden de Ejecución](#orden-de-ejecución)
- [Uso Detallado](#uso-detallado)
- [Resultados](#resultados)
- [Solución de Problemas](#solución-de-problemas)

## 🔧 Requisitos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)
- Sistema operativo: Windows, Linux o macOS

## 📦 Instalación de Paquetes

### Opción 1: Instalación Individual

```bash
pip install torch torchvision
pip install pandas
pip install numpy
pip install Pillow
pip install scikit-learn
pip install matplotlib
```

### Opción 2: Instalación en un Solo Comando

```bash
pip install torch torchvision pandas numpy Pillow scikit-learn matplotlib
```

### Verificar Instalación

Para verificar que todos los paquetes están instalados correctamente:

```bash
python -c "import torch; import pandas; import numpy; from PIL import Image; from sklearn.metrics import confusion_matrix; import matplotlib.pyplot as plt; print('✓ Todos los paquetes están instalados correctamente')"
```

## 📁 Estructura del Proyecto

```
algoritmo/
│
├── dataset/                    # Carpeta principal de imágenes
│   ├── healthy/                # Imágenes de gatos sanos
│   │   ├── gato1.jpg
│   │   ├── gato2.jpg
│   │   └── gato3.jpg
│   └── sick/                   # Imágenes de gatos enfermos
│       ├── gato4.jpg
│       ├── gato5.jpg
│       └── gato6.jpg
│
├── generate_csv.py            # Script 1: Genera el archivo CSV
├── train_cats_pytorch.py      # Script 2: Entrena el modelo
├── dataset.csv                # Archivo CSV generado (se crea automáticamente)
│
├── artifacts/                 # Carpeta de resultados (se crea automáticamente)
│   ├── best_model.pth         # Modelo entrenado guardado
│   ├── loss.png               # Gráfica de pérdida
│   └── acc.png                # Gráfica de precisión
│
├── training.log               # Archivo de log del entrenamiento
└── README.md                  # Este archivo
```

### Descripción de Carpetas

- **`dataset/`**: Contiene las imágenes organizadas en subcarpetas:
  - `healthy/`: Imágenes de gatos sanos (label: 0)
  - `sick/`: Imágenes de gatos enfermos (label: 1)
- **`artifacts/`**: Se crea automáticamente y contiene:
  - El modelo entrenado (`best_model.pth`)
  - Gráficas de entrenamiento (`loss.png`, `acc.png`)

## 🚀 Orden de Ejecución

### Paso 1: Preparar las Imágenes

Asegúrate de que tus imágenes estén organizadas en la estructura correcta:

```
dataset/
├── healthy/
│   └── [imágenes de gatos sanos]
└── sick/
    └── [imágenes de gatos enfermos]
```

**Formato de imágenes soportado**: `.jpg`, `.jpeg`, `.png`

### Paso 2: Generar el Archivo CSV

Ejecuta el primer script para crear el archivo `dataset.csv`:

```bash
python generate_csv.py
```

**¿Qué hace este script?**

- Recorre las carpetas `healthy/` y `sick/`
- Crea un archivo CSV con las rutas de las imágenes y sus etiquetas
- Formato del CSV: `image_path,label,timestamp,source`
  - `label`: 0 para healthy, 1 para sick

**Salida esperada:**

```
CSV creado exitosamente: dataset.csv
Total de imágenes procesadas: 6
```

### Paso 3: Entrenar el Modelo

Ejecuta el script de entrenamiento:

```bash
python train_cats_pytorch.py
```

**¿Qué hace este script?**

1. Carga el archivo `dataset.csv`
2. Normaliza las rutas de las imágenes
3. Verifica que todas las imágenes existan
4. Divide los datos en:
   - **Train**: 70% de las imágenes
   - **Validation**: 15% de las imágenes
   - **Test**: 15% de las imágenes
5. Entrena el modelo por 20 épocas
6. Guarda el mejor modelo en `artifacts/best_model.pth`
7. Genera gráficas de pérdida y precisión
8. Evalúa el modelo en el conjunto de test

**Salida esperada:**

```
Usando dispositivo: cpu
Cargando CSV: dataset.csv
Total de imágenes: 6
Train: 4, Val: 1, Test: 1

Iniciando entrenamiento...
Epoch 1/20 - train_loss 0.xxxx train_acc 0.xxxx - val_loss 0.xxxx val_acc 0.xxxx
Epoch 2/20 - train_loss 0.xxxx train_acc 0.xxxx - val_loss 0.xxxx val_acc 0.xxxx
...
Test loss: 0.xxxx
              precision    recall  f1-score   support

        sano       1.00      1.00      1.00         1
     enfermo       1.00      1.00      1.00         1

Entrenamiento completado exitosamente!
```

## 📖 Uso Detallado

### Configuración del Entrenamiento

Puedes modificar los parámetros en `train_cats_pytorch.py`:

```python
IMG_SIZE = 128      # Tamaño de las imágenes (128x128 píxeles)
BATCH = 16          # Tamaño del batch
EPOCHS = 20         # Número de épocas de entrenamiento
OUT_DIR = "artifacts"  # Directorio de salida
```

### Ejecución Completa desde Cero

```bash
# 1. Navegar al directorio del proyecto
cd "ruta/a/algoritmo"

# 2. Generar el CSV
python generate_csv.py

# 3. Entrenar el modelo
python train_cats_pytorch.py
```

## 📊 Resultados

Después de ejecutar `train_cats_pytorch.py`, encontrarás:

### Archivos Generados

1. **`artifacts/best_model.pth`**

   - Modelo entrenado guardado
   - Puede cargarse con: `torch.load('artifacts/best_model.pth')`

2. **`artifacts/loss.png`**

   - Gráfica que muestra la evolución de la pérdida durante el entrenamiento
   - Compara train_loss vs val_loss

3. **`artifacts/acc.png`**

   - Gráfica que muestra la evolución de la precisión durante el entrenamiento
   - Compara train_acc vs val_acc

4. **`training.log`**
   - Archivo de texto con todo el registro del entrenamiento
   - Incluye métricas de cada época

### Métricas de Evaluación

El script muestra al final:

- **Test Loss**: Pérdida en el conjunto de test
- **Classification Report**: Precisión, recall y F1-score por clase
- **Confusion Matrix**: Matriz de confusión

## 🔍 Solución de Problemas

### Error: "No module named 'torch'"

**Solución**: Instala PyTorch:

```bash
pip install torch torchvision
```

### Error: "No hay suficientes imágenes"

**Solución**: Asegúrate de tener al menos 3 imágenes en total. Con solo 6 imágenes, la división será:

- Train: 4 imágenes
- Val: 1 imagen
- Test: 1 imagen

### Error: "imágenes no encontradas"

**Solución**:

1. Verifica que las rutas en `dataset.csv` sean correctas
2. Asegúrate de ejecutar los scripts desde el directorio `algoritmo/`
3. El script normaliza automáticamente las rutas (Windows/Linux)

### Error: "CUDA out of memory"

**Solución**:

- Reduce el tamaño del batch: `BATCH = 8` o `BATCH = 4`
- Reduce el tamaño de las imágenes: `IMG_SIZE = 64`

### El script se ejecuta pero no veo salida

**Solución**:

- Revisa el archivo `training.log` que se genera automáticamente
- Todos los mensajes se guardan ahí

### Problemas con rutas en Windows

**Solución**: El script maneja automáticamente las barras invertidas (`\`) y barras normales (`/`). Si tienes problemas:

1. Asegúrate de que el CSV use rutas relativas: `dataset/healthy/gato1.jpg`
2. Ejecuta el script desde el directorio `algoritmo/`

## 📝 Notas Importantes

1. **Dataset pequeño**: Con solo 6 imágenes, el modelo puede sobreajustarse fácilmente. Se recomienda tener al menos 50-100 imágenes por clase para mejores resultados. En pruebas con 6 imágenes (3 sanas, 3 enfermas), el modelo alcanzó 100% de precisión, pero esto puede indicar sobreajuste.

2. **Data Augmentation**: El script incluye aumentación de datos (rotación, espejo) para mejorar el entrenamiento con datasets pequeños.

3. **División de datos**: Con muy pocas imágenes, la división 70/15/15 puede resultar en conjuntos muy pequeños. Con 6 imágenes: Train: 4, Val: 1, Test: 1. Considera ajustar estos porcentajes si tienes más datos.

4. **GPU**: Si tienes una GPU compatible con CUDA, el script la usará automáticamente. De lo contrario, usará CPU.

5. **Tiempo de ejecución**: Con 6 imágenes y 20 épocas, el entrenamiento toma aproximadamente 1-3 minutos en CPU.

## 🎯 Próximos Pasos

- Agregar más imágenes al dataset
- Experimentar con diferentes arquitecturas de red
- Ajustar hiperparámetros (learning rate, batch size, etc.)
- Implementar early stopping
- Agregar más técnicas de data augmentation

## 📄 Licencia

Este proyecto es para fines educativos.

---

**¿Problemas?** Revisa el archivo `training.log` para ver los detalles del error.
