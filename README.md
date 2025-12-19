# 🐱 Procesador de Imágenes con IA - Clasificación de Gatos

Aplicación web completa para clasificar imágenes de gatos como "sanos" (healthy) o "enfermos" (sick) usando inteligencia artificial. Incluye un modelo de deep learning entrenado con PyTorch, una API REST con FastAPI y un frontend React moderno.

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#descripción-del-proyecto)
- [Características](#características)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación y Configuración](#instalación-y-configuración)
- [Ejecución Local](#ejecución-local)
- [Despliegue en Producción](#despliegue-en-producción)
- [Uso de la Aplicación](#uso-de-la-aplicación)
- [Entrenamiento del Modelo](#entrenamiento-del-modelo)
- [Solución de Problemas](#solución-de-problemas)

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

⚠️ **IMPORTANTE**: El entrenamiento del modelo **NO se hace en Render** ni en otras plataformas de despliegue. Render es solo para desplegar la aplicación, no para entrenar modelos.

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

4. **Subir modelo al repositorio**:

   ```bash
   git add artifacts/best_model.pth
   git commit -m "Add trained model"
   git push
   ```

5. **Render desplegará automáticamente** el modelo junto con el código.

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

### Proceso Completo de Entrenamiento y Despliegue

```
1. Entrenar modelo (local/Colab/Kaggle)
   ↓
2. Obtener artifacts/best_model.pth
   ↓
3. Subir modelo al repositorio Git
   ↓
4. Hacer push al repositorio
   ↓
5. Render detecta cambios y despliega automáticamente
   ↓
6. El modelo ya está disponible en producción
```

### Requisitos para el Entrenamiento

- **Mínimo 3 imágenes** (para train/val/test split)
- **Recomendado**: Al menos 50-100 imágenes por clase para mejores resultados
- **Python 3.11 o 3.12** con PyTorch instalado
- **GPU opcional pero recomendada** para entrenamientos más rápidos

### Notas Importantes

- **Render NO entrena modelos**: Render solo despliega el modelo ya entrenado
- **El modelo debe estar en el repositorio**: Render copia todo el código, incluyendo `artifacts/best_model.pth`
- **Si no hay modelo**: La aplicación funcionará pero mostrará "no clasificado" para todas las imágenes
- **Modelos grandes**: Si el modelo es >100MB, considera usar Git LFS o subirlo manualmente después del despliegue

## 🌐 Despliegue en Producción

### Opción 1: Railway (Recomendado - Más Fácil)

Railway permite desplegar backend y frontend fácilmente.

#### Backend en Railway

1. **Crear cuenta** en [railway.app](https://railway.app)
2. **Nuevo proyecto** → "Deploy from GitHub repo" (o "Empty Project" para subir código)
3. **Agregar servicio** → "GitHub Repo" o "Empty Service"
4. **Si usas GitHub**: Selecciona tu repositorio
5. **Configurar servicio**:
   - Railway detectará automáticamente Python
   - **Variables de entorno** (Settings → Variables):
     ```
     PORT=8000
     ALLOWED_ORIGINS=https://tu-frontend.railway.app
     ```
6. Railway asignará una URL automáticamente (ej: `https://tu-backend.up.railway.app`)
7. **Copiar la URL** del backend para usarla en el frontend

#### Frontend en Railway

1. **Nuevo servicio** en el mismo proyecto Railway
2. **Agregar servicio** → "GitHub Repo" (mismo repo) o "Empty Service"
3. **Configurar**:
   - **Root Directory**: `frontend`
   - Railway detectará Node.js automáticamente
4. **Variables de entorno** (Settings → Variables):
   ```
   VITE_API_URL=https://tu-backend.up.railway.app
   PORT=3001
   ```
5. **Build Settings** (Settings → Build):
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npx serve -s dist -l $PORT`

**Nota importante**: Railway reconstruye automáticamente cuando cambias variables de entorno. Asegúrate de que `VITE_API_URL` tenga la URL correcta del backend antes del build.

### Opción 2: Render

#### Backend en Render

1. Crear cuenta en [render.com](https://render.com)
2. **New** → **Web Service**
3. Conectar repositorio GitHub
4. Configurar:
   - **Name**: `algoritmo-ia-backend`
   - **Environment**: **Python 3** ⚠️ **Importante**: Selecciona Python 3, NO Docker (a menos que tengas un Dockerfile específico)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables**:
   ```
   PORT=8000
   ALLOWED_ORIGINS=https://tu-frontend.onrender.com
   ```
6. Render asignará una URL (ej: `https://algoritmo-ia-backend.onrender.com`)

**Nota sobre Environment**: Si Render detecta automáticamente Docker, cámbialo a **Python 3**. Docker solo es necesario si tienes un `Dockerfile` en la raíz del proyecto y quieres usarlo. Para un despliegue simple, Python 3 es más fácil y rápido.

#### Frontend en Render

1. **New** → **Static Site**
2. Conectar repositorio GitHub
3. Configurar:
   - **Name**: `algoritmo-ia-frontend`
   - **Branch**: `main` (o tu rama principal)
   - **Root Directory**: `frontend` ⚠️ **Importante**: Configura esto primero
   - **Build Command**: `npm install && npm run build` ⚠️ Sin `cd frontend` ni `frontend/` ya que Root Directory ya está configurado
   - **Publish Directory**: `dist` ⚠️ Solo `dist`, no `frontend/dist` (es relativo al Root Directory)
4. **Environment Variables**:
   ```
   VITE_API_URL=https://algoritmo-ia-backend.onrender.com
   ```
5. Render asignará una URL automáticamente

**Nota importante**: Si configuraste **Root Directory** como `frontend`, entonces:

- **Build Command** debe ser: `npm install && npm run build` (sin `cd frontend` ni `frontend/`)
- **Publish Directory** debe ser: `dist` (no `frontend/dist`)

Si NO configuraste Root Directory, entonces:

- **Build Command**: `cd frontend && npm install && npm run build`
- **Publish Directory**: `frontend/dist`

### Opción 3: Vercel (Frontend) + Railway/Render (Backend)

Esta opción combina Vercel para el frontend (muy rápido y fácil) con Railway o Render para el backend.

#### Frontend en Vercel

1. Crear cuenta en [vercel.com](https://vercel.com)
2. **New Project** → Importar repositorio GitHub
3. Configurar:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (automático con Vite)
   - **Output Directory**: `dist` (automático)
4. **Environment Variables** (Settings → Environment Variables):
   ```
   VITE_API_URL=https://tu-backend.railway.app
   ```
   **Importante**: Agrega esta variable para **Production**, **Preview** y **Development**
5. **Deploy**: Vercel desplegará automáticamente
6. Vercel asignará una URL (ej: `https://algoritmo-ia.vercel.app`)

**Ventajas de Vercel**:

- Despliegue muy rápido
- CDN global automático
- Reconstrucción automática en cada push
- Preview deployments para cada PR

### Opción 4: Docker Compose (VPS/Cloud/Servidor Propio)

#### Backend Dockerfile

Crear `Dockerfile` en la raíz:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Crear directorios necesarios
RUN mkdir -p uploads outputs artifacts

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### Frontend Dockerfile

Crear `frontend/Dockerfile`:

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### docker-compose.yml

```yaml
version: "3.8"

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
    volumes:
      - ./uploads:/app/uploads
      - ./outputs:/app/outputs
      - ./artifacts:/app/artifacts
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3001:80"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped
```

**Desplegar**:

```bash
docker-compose up -d
```

**Ver logs**:

```bash
docker-compose logs -f
```

**Detener**:

```bash
docker-compose down
```

**Actualizar**:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Configuración de Variables de Entorno en Producción

#### Backend

**Railway/Render**:

```env
PORT=8000
ALLOWED_ORIGINS=https://tu-frontend.vercel.app,https://tu-dominio.com
```

**Nota**: En Railway y Render, `PORT` se asigna automáticamente, pero puedes especificarlo.

#### Frontend

**Vercel/Railway/Render**:

```env
VITE_API_URL=https://tu-backend.railway.app
```

**Importante**:

- En Vercel, agrega la variable en **Settings → Environment Variables**
- Selecciona todos los ambientes (Production, Preview, Development)
- Vercel reconstruirá automáticamente después de agregar variables

### Incluir el Modelo Entrenado en el Despliegue

⚠️ **PASO CRÍTICO**: Para que la clasificación funcione en producción, el modelo debe estar entrenado e incluido en el repositorio.

**Proceso**:

1. **Entrenar el modelo** (ver sección [Entrenamiento del Modelo](#-entrenamiento-del-modelo))

   - Entrena localmente, en Colab, o en otra plataforma
   - Obtén `artifacts/best_model.pth`

2. **Subir el modelo al repositorio**:

   ```bash
   git add artifacts/best_model.pth
   git commit -m "Add trained model"
   git push
   ```

3. **Render desplegará automáticamente** el modelo junto con el código

**Si el modelo es muy grande** (>100MB):

- **Opción 1**: Usar Git LFS (recomendado)

  ```bash
  git lfs install
  git lfs track "*.pth"
  git add .gitattributes
  git add artifacts/best_model.pth
  git commit -m "Add trained model with LFS"
  git push
  ```

- **Opción 2**: Subir manualmente después del despliegue

  - Despliega primero sin el modelo
  - Usa el shell de Render o SCP para subir el archivo
  - Colócalo en `artifacts/best_model.pth`

- **Opción 3**: Usar almacenamiento externo (S3, Google Cloud Storage)
  - Modifica `predict.py` para descargar el modelo desde el almacenamiento
  - Más complejo pero escalable

**Nota**: Si no incluyes el modelo, la aplicación funcionará pero mostrará "no clasificado" para todas las imágenes. El backend mostrará un mensaje de advertencia en los logs.

### Checklist de Despliegue

- [ ] Backend desplegado y accesible
- [ ] Frontend configurado con `VITE_API_URL` correcta
- [ ] CORS configurado en backend con URL del frontend
- [ ] Modelo entrenado (`artifacts/best_model.pth`) incluido en el despliegue
- [ ] Variables de entorno configuradas
- [ ] Probar subida de imágenes
- [ ] Probar descarga de CSV
- [ ] Verificar que las clasificaciones funcionen

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

### Problemas en Railway/Render

**Build falla**:

- Verifica que todas las dependencias estén en `requirements.txt`
- Revisa los logs de build en la plataforma

**Frontend no encuentra el backend**:

- Usa la URL completa del backend en `VITE_API_URL`
- Reconstruye el frontend después de cambiar variables de entorno

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

- **API Docs**: `http://localhost:8000/docs` (cuando el backend esté corriendo)
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📄 Licencia

Este proyecto es para fines educativos.

---

**¿Problemas?** Revisa los logs del backend o frontend, o consulta la sección de [Solución de Problemas](#solución-de-problemas).
