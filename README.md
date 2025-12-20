# 🐱 Procesador de Imágenes con IA - Clasificación de Gatos

Aplicación web completa para clasificar imágenes de gatos como "sanos" (healthy) o "enfermos" (sick) usando inteligencia artificial. Incluye un modelo de deep learning entrenado con PyTorch, una API REST con FastAPI y un frontend React moderno.

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#descripción-del-proyecto)
- [Características](#características)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación y Configuración](#instalación-y-configuración)
- [Ejecución Local](#ejecución-local)
- [Uso de la Aplicación](#uso-de-la-aplicación)
- [Entrenamiento del Modelo](#entrenamiento-del-modelo)
- [Aprendizaje Continuo](#aprendizaje-continuo-continual-learning)
- [Endpoints de la API](#endpoints-de-la-api)
- [Solución de Problemas](#solución-de-problemas)
- [Despliegue en Producción](#despliegue-en-producción)

## 🎯 Descripción del Proyecto

Este proyecto es una aplicación web completa que permite:

1. **Entrenar un modelo de IA** para clasificar gatos como sanos o enfermos
2. **Procesar imágenes** subidas por usuarios a través de una interfaz web
3. **Clasificar automáticamente** cada imagen usando el modelo entrenado
4. **Generar archivos CSV** con los resultados de la clasificación
5. **Visualizar resultados** en una tabla interactiva o lista

### Arquitectura

```
┌─────────────────┐
│  Frontend React │  (Puerto 3001)
│  (Vite + React) │
└────────┬────────┘
         │ HTTP Requests
         │
┌────────▼────────┐
│  Backend FastAPI│  (Puerto 8000)
│  (Python)       │
└────────┬────────┘
         │
         │ Usa modelo entrenado
         │
┌────────▼────────┐
│  Modelo PyTorch │
│  (SimpleCNN)    │
└─────────────────┘
```

## ✨ Características

### Backend (FastAPI)

- ✅ API REST para procesar múltiples imágenes
- ✅ Clasificación automática con modelo de IA
- ✅ Generación de archivos CSV con resultados
- ✅ Validación de tipos y tamaños de archivo
- ✅ CORS configurado para frontend
- ✅ Documentación interactiva (Swagger/ReDoc)

### Frontend (React)

- ✅ Interfaz moderna y responsive
- ✅ Carga múltiple de imágenes (drag & drop)
- ✅ Visualización de resultados en tabla y lista
- ✅ Descarga de CSV con resultados
- ✅ Indicadores de progreso
- ✅ Manejo de errores

### Modelo de IA

- ✅ Red neuronal convolucional (CNN) con PyTorch
- ✅ Clasificación binaria: sano (0) vs enfermo (1)
- ✅ Data augmentation para mejorar entrenamiento
- ✅ Métricas de evaluación (precisión, recall, F1-score)

## 📁 Estructura del Proyecto

```
algoritmo_ia/
│
├── main.py                    # Backend API FastAPI
├── predict.py                 # Módulo de predicción con modelo IA
├── generate_csv.py            # Script para generar CSV desde dataset/
├── train_cats_pytorch.py      # Script para entrenar el modelo
├── requirements.txt           # Dependencias Python
│
├── frontend/                  # Frontend React
│   ├── src/
│   │   ├── api/              # Cliente API
│   │   ├── components/        # Componentes React
│   │   ├── hooks/             # Custom hooks
│   │   ├── pages/             # Páginas
│   │   └── types.ts           # Tipos TypeScript
│   ├── package.json
│   └── vite.config.ts
│
├── dataset/                   # Dataset de entrenamiento (opcional)
│   ├── healthy/               # Imágenes de gatos sanos
│   └── sick/                  # Imágenes de gatos enfermos
│
├── artifacts/                 # Modelo entrenado (se crea al entrenar)
│   ├── best_model.pth         # Modelo guardado
│   ├── loss.png               # Gráfica de pérdida
│   └── acc.png                # Gráfica de precisión
│
├── uploads/                   # Archivos temporales subidos (se crea automáticamente)
├── outputs/                   # CSVs generados (se crea automáticamente)
│
└── README.md                  # Este archivo
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- **Python 3.11 o 3.12** (recomendado) para el backend
  - Python 3.14+ puede tener problemas con algunas dependencias
  - Si usas Python 3.14+, ver [Solución de Problemas](#problemas-de-instalación)
- **Node.js 18+** y npm para el frontend
- **Git** (opcional)

### 1. Clonar o descargar el proyecto

```bash
cd "C:\Users\eadel\OneDrive\Documents\universidad\Electiva Inteligencia artificial avanzada\algoritmo_ia"
```

### 2. Configurar Backend

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Actualizar pip, setuptools y wheel
python -m pip install --upgrade pip setuptools wheel

# Instalar dependencias
pip install -r requirements.txt
```

**Nota sobre problemas de instalación**:

Si tienes problemas instalando `pydantic-core` (error sobre Rust/Cargo):

- **Opción 1**: Usa Python 3.11 o 3.12 (más compatible, tiene wheels precompilados)
- **Opción 2**: Instala pydantic desde wheels: `pip install pydantic --only-binary :all:`
- **Opción 3**: Usa `requirements-minimal.txt`: `pip install -r requirements-minimal.txt`
- **Opción 4**: Si usas Anaconda, puedes instalar desde conda: `conda install -c conda-forge pydantic`

### 3. Configurar Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Crear archivo de configuración
echo "VITE_API_URL=http://localhost:8000" > .env
```

## 🏃 Ejecución Local

### Opción 1: Ejecutar Backend y Frontend por separado

**Terminal 1 - Backend:**

```bash
# Desde la raíz del proyecto
python main.py
```

El backend estará disponible en: `http://localhost:8000`

- API: `http://localhost:8000`
- Documentación: `http://localhost:8000/docs`

**Terminal 2 - Frontend:**

```bash
# Desde la carpeta frontend
cd frontend
npm run dev
```

El frontend estará disponible en: `http://localhost:3001`

### Opción 2: Usar scripts de inicio rápido

Puedes crear scripts para iniciar ambos servicios simultáneamente.

## 🎨 Uso de la Aplicación

1. **Abrir la aplicación**: Navega a `http://localhost:3001`
2. **Subir imágenes**: Arrastra imágenes o haz clic para seleccionar
3. **Procesar**: Haz clic en "Procesar Imágenes"
4. **Ver resultados**: Los resultados se muestran en tabla o lista
5. **Descargar CSV**: Haz clic en "Descargar CSV" para obtener los resultados

### Formato de Imágenes Soportado

- JPG, JPEG, PNG, GIF, BMP, WEBP
- Tamaño máximo: 10MB por archivo

## 🧠 Entrenamiento del Modelo

⚠️ **IMPORTANTE**: El entrenamiento del modelo **NO se hace en plataformas de despliegue** (Render, Railway, etc.). Estas plataformas son solo para desplegar la aplicación, no para entrenar modelos.

### ¿Dónde entrenar el modelo?

Tienes varias opciones para entrenar el modelo:

#### Opción 1: Entrenar Localmente (Recomendado para empezar)

**Ventajas**: Gratis, control total, fácil de depurar

**Pasos**:

1. **Preparar Dataset**: Organiza tus imágenes en:

   ```
   dataset/
   ├── healthy/    # Gatos sanos (label: 0)
   └── sick/       # Gatos enfermos (label: 1)
   ```

2. **Generar CSV**:

   ```bash
   python generate_csv.py
   ```

   Esto crea `dataset.csv` con las rutas y etiquetas.

3. **Entrenar Modelo**:

   ```bash
   python train_cats_pytorch.py
   ```

   El modelo entrenado se guardará en `artifacts/best_model.pth`

4. **Incluir el modelo en el proyecto**:

   ```bash
   git add artifacts/best_model.pth
   git commit -m "Add trained model"
   git push
   ```

   El modelo se incluirá en el despliegue automáticamente.

#### Opción 2: Google Colab (Gratis con GPU)

**Ventajas**: GPU gratuita, no necesitas instalar nada localmente

**Pasos**:

1. Abre [Google Colab](https://colab.research.google.com/)
2. Sube tu proyecto o clona desde GitHub
3. Ejecuta los mismos pasos (generate_csv.py y train_cats_pytorch.py)
4. Descarga `artifacts/best_model.pth` desde Colab
5. Súbelo a tu repositorio local y haz commit

#### Opción 3: Kaggle Notebooks (Gratis con GPU)

**Ventajas**: GPU gratuita, comunidad activa

**Pasos similares a Colab**

#### Opción 4: VPS con GPU (AWS, Google Cloud, etc.)

**Ventajas**: Más control, mejor para datasets grandes

**Desventajas**: Requiere configuración y puede tener costos

### Requisitos para el Entrenamiento

- **Mínimo 3 imágenes** (para train/val/test split)
- **Recomendado**: Al menos 50-100 imágenes por clase para mejores resultados
- **Python 3.11 o 3.12** con PyTorch instalado
- **GPU opcional pero recomendada** para entrenamientos más rápidos

### Notas Importantes

- **El modelo debe estar entrenado antes del despliegue**: El archivo `artifacts/best_model.pth` debe existir
- **Si no hay modelo**: La aplicación funcionará pero mostrará "no clasificado" para todas las imágenes
- **Modelos grandes**: Si el modelo es >100MB, considera usar Git LFS (ver [DEPLOYMENT.md](./DEPLOYMENT.md))
- **Para incluir el modelo en el despliegue**: Consulta la sección "Incluir el Modelo Entrenado" en [DEPLOYMENT.md](./DEPLOYMENT.md)

## 🔄 Aprendizaje Continuo (Continual Learning)

El sistema incluye funcionalidad de **aprendizaje continuo** que permite mejorar el modelo automáticamente con las imágenes que los usuarios suben y procesan.

### ¿Cómo funciona?

1. **Almacenamiento automático**: Cada vez que se procesa una imagen, el sistema guarda automáticamente:

   - La imagen procesada
   - La clasificación predicha por el modelo
   - El nivel de confianza

2. **Correcciones de usuarios**: Los usuarios pueden corregir clasificaciones incorrectas:

   - En la tabla de resultados, cada imagen tiene un botón "Corregir"
   - Al hacer clic, se abre un modal para seleccionar la clasificación correcta
   - Las correcciones se guardan para reentrenamiento

3. **Reentrenamiento incremental**: El modelo se puede reentrenar periódicamente:
   - Combina datos originales con feedback de usuarios
   - Usa fine-tuning (aprendizaje de transferencia) para mejorar sin perder conocimiento previo
   - Guarda backups del modelo anterior por seguridad

### Configuración del Aprendizaje Continuo

#### Opción 1: Reentrenamiento Manual

Ejecuta el script de reentrenamiento cuando tengas suficientes correcciones:

```bash
# Reentrenar con mínimo 10 imágenes de feedback
python incremental_train.py --epochs 10 --min-feedback 10
```

#### Opción 2: Reentrenamiento Automático (Cron Job)

En producción, puedes configurar un cron job o tarea programada:

**Linux/Mac (cron)**:

```bash
# Reentrenar cada domingo a las 2 AM
0 2 * * 0 cd /ruta/al/proyecto && python incremental_train.py --epochs 10 --min-feedback 20
```

**Windows (Task Scheduler)**:

- Crear tarea programada que ejecute: `python incremental_train.py --epochs 10 --min-feedback 20`

**En Producción**:

- Consulta [DEPLOYMENT.md](./DEPLOYMENT.md) para configurar cron jobs en diferentes plataformas
- Usa el endpoint `/api/v1/model/retrain` desde un servicio externo

#### Opción 3: Reentrenamiento desde la API

Puedes disparar el reentrenamiento mediante la API:

```bash
curl -X POST "https://tu-backend.com/api/v1/model/retrain?epochs=10&min_feedback=10"
```

**⚠️ Nota**: En producción, el reentrenamiento puede tomar tiempo. Consulta [DEPLOYMENT.md](./DEPLOYMENT.md) para consideraciones específicas de cada plataforma.

### Estructura de Datos de Feedback

Los datos se almacenan en:

- `feedback_data/feedback.csv`: Historial completo de procesamientos y correcciones
- `feedback_data/images/`: Imágenes organizadas por clase (healthy/sick)

### Endpoints de Aprendizaje Continuo

- `POST /api/v1/feedback/correct`: Corregir una clasificación

  ```json
  {
    "image_path": "uploads/imagen.jpg",
    "corrected_label": 0,
    "corrected_label_name": "sano",
    "user_feedback": "El gato está sano"
  }
  ```

- `GET /api/v1/feedback/stats`: Obtener estadísticas de feedback

  ```json
  {
    "total_images": 150,
    "corrections": 12,
    "accuracy_estimate": 0.92
  }
  ```

- `POST /api/v1/model/retrain`: Disparar reentrenamiento
  - Parámetros: `epochs` (default: 10), `min_feedback` (default: 10)

### Mejores Prácticas

1. **Mínimo de correcciones**: Espera al menos 20-50 correcciones antes de reentrenar
2. **Validación**: Siempre valida el modelo en un conjunto de test después del reentrenamiento
3. **Backups**: El sistema guarda backups automáticamente en `artifacts/backups/`
4. **Monitoreo**: Revisa las estadísticas de feedback para detectar problemas
5. **Calidad de datos**: Asegúrate de que las correcciones sean precisas antes de reentrenar

## 🌐 Despliegue en Producción

Para información completa sobre cómo desplegar este proyecto en producción, consulta la **[Guía de Despliegue](./DEPLOYMENT.md)**.

La guía incluye instrucciones detalladas para:

- ✅ **Plan de $25 USD en Render** - Análisis completo de recursos y configuración
- ✅ **Despliegue en WHM** - Guía paso a paso para servidor propio
- ✅ **Railway, Render, Vercel** - Configuración para cada plataforma
- ✅ **Docker Compose** - Despliegue con contenedores
- ✅ **Consideraciones de Reentrenamiento** - Almacenamiento persistente, recursos, timeouts
- ✅ **Checklist completo** - Verificación paso a paso

**Resumen rápido:**

- **Render $25/mes**: ✅ Funciona con disco persistente agregado
- **WHM/Servidor Propio**: ✅ Mejor opción para reentrenamiento sin limitaciones
- **Railway**: ✅ Recomendado para empezar, soporta volúmenes persistentes

## 📡 Endpoints de la API

### Health Check

- `GET /` - Estado del servicio
- `GET /health` - Health check

### Procesamiento

- `POST /api/v1/images/process` - Procesa imágenes y genera CSV
  - Body: `multipart/form-data` con archivos
  - Response: JSON con clasificaciones y URL del CSV

### Descarga

- `GET /api/v1/files/download/{filename}` - Descarga CSV generado
- `DELETE /api/v1/files/{filename}` - Elimina archivo

### Aprendizaje Continuo

- `POST /api/v1/feedback/correct` - Corregir una clasificación
  - Body: JSON con `image_path`, `corrected_label`, `corrected_label_name`, `user_feedback`
  - Response: JSON con confirmación
- `GET /api/v1/feedback/stats` - Estadísticas de feedback
  - Response: JSON con total de imágenes, correcciones y precisión estimada
- `POST /api/v1/model/retrain` - Disparar reentrenamiento incremental
  - Parámetros: `epochs` (int), `min_feedback` (int)
  - Response: JSON con resultado del reentrenamiento

## 🔧 Solución de Problemas

### Problemas de Instalación

**Error**: `pydantic-core` requiere Rust/Cargo para compilar

Este error ocurre cuando `pydantic-core` no tiene wheels precompilados para tu versión de Python (especialmente Python 3.14+).

**Soluciones**:

1. **Usar Python 3.11 o 3.12** (recomendado):

   ```bash
   # Crear nuevo entorno virtual con Python 3.11/3.12
   python3.11 -m venv venv
   # o
   python3.12 -m venv venv
   ```

2. **Instalar pydantic desde wheels precompilados**:

   ```bash
   pip install pydantic --only-binary :all:
   pip install -r requirements.txt
   ```

3. **Usar requirements-minimal.txt** (versiones flexibles):

   ```bash
   pip install -r requirements-minimal.txt
   ```

4. **Si usas Anaconda**:
   ```bash
   conda install -c conda-forge pydantic fastapi uvicorn
   pip install torch torchvision
   ```

### Backend no inicia

**Error**: `ModuleNotFoundError: No module named 'torch'`

```bash
pip install -r requirements.txt
```

**Error**: `Modelo no encontrado`

- Asegúrate de tener `artifacts/best_model.pth`
- O entrena el modelo primero: `python train_cats_pytorch.py`

### Frontend no se conecta al backend

**Error de CORS**:

- Verifica que `ALLOWED_ORIGINS` en `main.py` incluya la URL del frontend
- En desarrollo: `["http://localhost:3001"]`
- En producción: `["https://tu-frontend.vercel.app"]`

**Error de conexión**:

- Verifica `VITE_API_URL` en `.env` del frontend
- Asegúrate de que el backend esté corriendo

### El modelo no clasifica

- Verifica que `artifacts/best_model.pth` exista
- Revisa los logs del backend para errores de carga del modelo
- Asegúrate de que PyTorch esté instalado: `pip install torch torchvision`

### Problemas de Despliegue

Para problemas específicos de despliegue en Railway, Render, WHM u otras plataformas, consulta la sección de **Troubleshooting** en [DEPLOYMENT.md](./DEPLOYMENT.md).

## 📊 Resultados y CSV

El CSV generado tiene el formato:

```csv
image_path,label,timestamp,source,label_name
uploads/imagen1.jpg,0,2024-01-15T10:30:00,api_upload,sano
uploads/imagen2.jpg,1,2024-01-15T10:30:01,api_upload,enfermo
```

- `label`: 0 para sano, 1 para enfermo
- `label_name`: "sano" o "enfermo" en español

## 🎯 Próximos Pasos

- [ ] Agregar autenticación si es necesario
- [ ] Implementar rate limiting
- [ ] Agregar más métricas de evaluación
- [ ] Mejorar el modelo con más datos
- [ ] Agregar historial de procesamientos

## 📚 Documentación Adicional

- **[Guía de Despliegue](./DEPLOYMENT.md)** - Instrucciones completas para desplegar en producción (Render, WHM, Railway, Docker, etc.)
- **API Docs**: `http://localhost:8000/docs` (cuando el backend esté corriendo)
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📄 Licencia

Este proyecto es para fines educativos.

---

**¿Problemas?** Revisa los logs del backend o frontend, o consulta la sección de [Solución de Problemas](#solución-de-problemas).
