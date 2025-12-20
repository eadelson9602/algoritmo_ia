# 🚀 Guía de Despliegue en Producción

Esta guía contiene todas las instrucciones para desplegar el proyecto **Procesador de Imágenes con IA** en diferentes plataformas de producción.

## 📋 Tabla de Contenidos

- [Despliegue en WHM (Web Host Manager) - Backend](#-despliegue-en-whm-web-host-manager---backend)
- [Despliegue en WHM con Docker (Recomendado para CentOS 7)](#-despliegue-en-whm-con-docker-recomendado-para-centos-7)
- [Despliegue en Railway](#-opción-1-railway-recomendado---más-fácil)
- [Despliegue en Render](#-opción-2-render)
- [Despliegue en Vercel + Railway/Render](#-opción-3-vercel-frontend--railwayrender-backend)
- [Despliegue con Docker Compose](#-opción-4-docker-compose-vpscloudservidor-propio)
- [Consideraciones para Reentrenamiento](#-consideraciones-especiales-para-reentrenamiento-en-producción)
- [Checklist de Despliegue](#-checklist-de-despliegue)

## 🖥️ Despliegue en WHM (Web Host Manager) - Backend

Esta guía te permitirá desplegar el **backend** del proyecto con reentrenamiento en tu servidor propio gestionado por WHM/cPanel, aprovechando todas las características sin limitaciones de recursos.

### 📋 Resumen Ejecutivo

**¿Qué necesitas?**

- Servidor con WHM/cPanel
- Acceso SSH
- Python 3.11/3.12
- Mínimo 2 GB RAM, 2 CPU cores, 10 GB disco

**Pasos principales:**

1. ✅ Configurar dominio/subdominio en WHM
2. ✅ Instalar Python en el servidor
3. ✅ Clonar proyecto y configurar entorno virtual
4. ✅ Crear servicio systemd para el backend
5. ✅ Configurar Apache como proxy reverso
6. ✅ Configurar cron job para reentrenamiento automático

**Resultado:**

- ✅ Backend funcionando en `https://api.tu-dominio.com`
- ✅ Reentrenamiento automático configurado
- ✅ Almacenamiento persistente garantizado
- ✅ Sin limitaciones de recursos

**Tiempo estimado:** 1 hora

### ✅ Ventajas de WHM para este Proyecto

- ✅ **Almacenamiento persistente garantizado** - Los datos NO se pierden
- ✅ **Sin límites de recursos** (depende de tu servidor)
- ✅ **Control total** sobre CPU, RAM y almacenamiento
- ✅ **Reentrenamiento sin restricciones** - Puedes usar todos los recursos disponibles
- ✅ **Sin timeouts** - Procesos largos funcionan sin problemas
- ✅ **Puedes usar GPU** si tu servidor tiene una disponible

### Prerrequisitos

1. **Acceso a WHM** (Web Host Manager)
2. **Acceso SSH** al servidor (recomendado)
3. **Python 3.11 o 3.12** instalado en el servidor
4. **Dominio o subdominio** configurado en WHM (ej: `api.tu-dominio.com`)
5. **Recursos del servidor**:
   - Mínimo 2 GB RAM (4 GB+ recomendado para reentrenamiento)
   - Mínimo 2 CPU cores (más cores = reentrenamiento más rápido)
   - Al menos 10 GB espacio en disco (para modelos, feedback, backups)

### Paso 1: Preparar el Entorno en el Servidor

#### 1.1. Acceder al Servidor vía SSH

```bash
ssh usuario@tu-servidor.com
```

#### 1.2. Verificar Python

```bash
python3 --version  # Debe ser 3.11 o 3.12
python3 -m pip --version
```

Si Python no está instalado o es una versión incorrecta:

```bash
# Opción 1: Usando pyenv (recomendado)
curl https://pyenv.run | bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc
pyenv install 3.12.0
pyenv global 3.12.0

# Opción 2: Compilar desde fuente (si pyenv no funciona)
# Consulta la documentación de tu distribución Linux
```

### Paso 2: Configurar el Dominio/Subdominio en WHM

#### 2.1. Crear o Configurar la Cuenta en WHM

1. Accede a **WHM** → **Account Functions** → **Create a New Account**
2. Completa los campos:
   - **Domain**: `tu-dominio.com` o `ia.tu-dominio.com`
   - **Username**: Nombre de usuario para la cuenta
   - **Password**: Contraseña segura
   - **Email**: Tu email de contacto
   - **Package**: Selecciona un paquete con recursos suficientes

#### 2.2. Configurar el Document Root

El backend se ejecutará como servicio systemd, no necesita Document Root. El dominio/subdominio se usará para el proxy reverso de Apache que apuntará al servicio backend.

### Paso 3: Preparar el Proyecto

#### 3.1. Clonar o Subir el Proyecto

**Opción A: Usando Git (Recomendado)**

```bash
cd /home/usuario/
git clone https://github.com/tu-repo/algoritmo_ia.git
cd algoritmo_ia
```

**Opción B: Subir vía SFTP**

1. Comprime el proyecto localmente
2. Súbelo vía SFTP a `/home/usuario/algoritmo_ia/`
3. Descomprime en el servidor

#### 3.2. Configurar Backend

```bash
cd /home/usuario/algoritmo_ia

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Actualizar pip
python -m pip install --upgrade pip setuptools wheel

# Instalar dependencias
pip install -r requirements.txt
```

**Nota**: Si tienes problemas con PyTorch, instálalo específicamente:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

#### 3.3. Verificar que el Modelo Esté Presente

```bash
# Verificar que el modelo existe
ls -lh artifacts/best_model.pth

# Si no existe, necesitas entrenarlo primero (ver README.md)
```

#### 3.4. Crear Directorios Necesarios

```bash
mkdir -p uploads outputs artifacts/backups feedback_data/images
chmod -R 755 uploads outputs artifacts feedback_data
```

### Paso 4: Configurar el Backend con Systemd (Recomendado)

#### 4.1. Crear Servicio Systemd

Crea el archivo `/etc/systemd/system/algoritmo-ia-backend.service`:

```ini
[Unit]
Description=Algoritmo IA Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=usuario
WorkingDirectory=/home/usuario/algoritmo_ia
Environment="PATH=/home/usuario/algoritmo_ia/venv/bin"
ExecStart=/home/usuario/algoritmo_ia/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Nota**: Ajusta `User=usuario` con tu usuario real.

#### 4.2. Activar y Iniciar el Servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable algoritmo-ia-backend
sudo systemctl start algoritmo-ia-backend
sudo systemctl status algoritmo-ia-backend
```

#### 4.3. Ver Logs del Backend

```bash
sudo journalctl -u algoritmo-ia-backend -f
```

### Paso 5: Configurar Apache como Proxy Reverso

#### 5.1. Habilitar Módulos Necesarios

En WHM:

1. Ve a **Software** → **EasyApache 4** (o **Apache Configuration**)
2. Asegúrate de que estos módulos estén habilitados:
   - `mod_proxy`
   - `mod_proxy_http`
   - `mod_rewrite`
   - `mod_ssl` (para HTTPS)

#### 5.2. Configurar Virtual Host para Backend

Crea o edita el archivo de configuración de Apache. En WHM:

1. Ve a **Service Configuration** → **Apache Configuration** → **Include Editor**
2. Selecciona **All Versions** → **Pre VirtualHost Include**
3. Agrega la configuración del proxy:

```apache
# Proxy para backend API
<VirtualHost *:80>
    ServerName api.tu-dominio.com

    ProxyPreserveHost On
    ProxyPass / http://localhost:8000/
    ProxyPassReverse / http://localhost:8000/

    # Headers necesarios
    RequestHeader set X-Forwarded-Proto "http"
    RequestHeader set X-Forwarded-Port "80"
</VirtualHost>
```

#### 5.3. Configurar SSL/HTTPS

En WHM:

1. Ve a **SSL/TLS** → **Install an SSL Certificate on a Domain**
2. Selecciona tu dominio (api.tu-dominio.com)
3. Opciones:
   - **Let's Encrypt** (gratis, recomendado)
   - **AutoSSL** (si está disponible)
   - Certificado propio

Después de instalar SSL, actualiza la configuración del VirtualHost para usar HTTPS:

```apache
<VirtualHost *:443>
    ServerName api.tu-dominio.com
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/tu-dominio.crt
    SSLCertificateKeyFile /etc/ssl/private/tu-dominio.key

    ProxyPreserveHost On
    ProxyPass / http://localhost:8000/
    ProxyPassReverse / http://localhost:8000/

    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Forwarded-Port "443"
</VirtualHost>
```

### Paso 6: Configurar Reentrenamiento Automático (Cron Job)

#### 7.1. Crear Script de Reentrenamiento

Crea `/home/usuario/algoritmo_ia/retrain_cron.sh`:

```bash
#!/bin/bash
cd /home/usuario/algoritmo_ia
source venv/bin/activate

# Reentrenar solo si hay suficiente feedback (mínimo 20 imágenes)
python incremental_train.py --epochs 5 --min-feedback 20

# Reiniciar el servicio para cargar el nuevo modelo
sudo systemctl restart algoritmo-ia-backend
```

Hacer ejecutable:

```bash
chmod +x /home/usuario/algoritmo_ia/retrain_cron.sh
```

#### 6.2. Configurar Cron Job

```bash
crontab -e
```

Agrega una línea para reentrenar periódicamente (ejemplo: cada domingo a las 2 AM):

```cron
0 2 * * 0 /home/usuario/algoritmo_ia/retrain_cron.sh >> /home/usuario/algoritmo_ia/retrain.log 2>&1
```

O reentrenar diariamente a las 3 AM:

```cron
0 3 * * * /home/usuario/algoritmo_ia/retrain_cron.sh >> /home/usuario/algoritmo_ia/retrain.log 2>&1
```

### Paso 7: Configurar Permisos y Seguridad

#### 7.1. Permisos de Archivos

```bash
# Backend
chown -R usuario:usuario /home/usuario/algoritmo_ia/
chmod -R 755 /home/usuario/algoritmo_ia/
chmod -R 777 /home/usuario/algoritmo_ia/uploads
chmod -R 777 /home/usuario/algoritmo_ia/outputs
chmod -R 755 /home/usuario/algoritmo_ia/artifacts
chmod -R 755 /home/usuario/algoritmo_ia/feedback_data
```

#### 7.2. Firewall (Opcional pero Recomendado)

Si tienes acceso a configuración de firewall:

```bash
# Permitir solo puertos necesarios
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp  # SSH
sudo ufw enable
```

### Paso 8: Verificar el Despliegue

1. **Verificar Backend**:

   ```bash
   curl https://api.tu-dominio.com/health
   ```

2. **Ver Documentación de la API**:

   - Abre `https://api.tu-dominio.com/docs` en el navegador
   - Verifica que la documentación interactiva (Swagger) esté disponible

3. **Probar Endpoints**:

   ```bash
   # Health check
   curl https://api.tu-dominio.com/

   # Probar endpoint de procesamiento (requiere imágenes)
   # Usa la documentación en /docs para probar los endpoints
   ```

4. **Probar Reentrenamiento**:
   ```bash
   # Reentrenamiento manual
   cd /home/usuario/algoritmo_ia
   source venv/bin/activate
   python incremental_train.py --epochs 5 --min-feedback 10
   ```

### Paso 9: Monitoreo y Mantenimiento

#### 9.1. Ver Logs

```bash
# Logs del backend
sudo journalctl -u algoritmo-ia-backend -f

# Logs de Apache
tail -f /usr/local/apache/logs/error_log
tail -f /usr/local/apache/logs/access_log

# Logs de reentrenamiento
tail -f /home/usuario/algoritmo_ia/retrain.log
```

#### 9.2. Actualizar la Aplicación

```bash
cd /home/usuario/algoritmo_ia

# Si usas Git
git pull

# Actualizar dependencias si es necesario
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar servicio
sudo systemctl restart algoritmo-ia-backend
```

##### 9.3. Backups

Configura backups automáticos en WHM:

1. Ve a **Backup** → **Backup Configuration**
2. Configura backups de:
   - `/home/usuario/algoritmo_ia/artifacts/` (modelos)
   - `/home/usuario/algoritmo_ia/feedback_data/` (feedback)
   - `/home/usuario/algoritmo_ia/` (código)

### Troubleshooting WHM

#### Backend no inicia

```bash
# Verificar estado
sudo systemctl status algoritmo-ia-backend

# Ver logs detallados
sudo journalctl -u algoritmo-ia-backend -n 50

# Verificar que Python y dependencias estén instaladas
source /home/usuario/algoritmo_ia/venv/bin/activate
python -c "import torch; print(torch.__version__)"
```

#### Error de permisos

```bash
# Verificar propietario
ls -la /home/usuario/algoritmo_ia/

# Corregir permisos
sudo chown -R usuario:usuario /home/usuario/algoritmo_ia/
```

#### Reentrenamiento falla

- Verifica que haya suficiente espacio en disco: `df -h`
- Verifica que haya suficiente RAM: `free -h`
- Revisa los logs: `tail -f /home/usuario/algoritmo_ia/retrain.log`

## 🐳 Despliegue en WHM con Docker (Recomendado para CentOS 7)

Si tienes **CentOS 7.9** (que solo incluye Python 3.6), la mejor opción es usar **Docker** para evitar problemas de versiones de Python.

### ✅ Ventajas de Docker en WHM

- ✅ **No necesitas instalar Python 3.12 manualmente** - Docker lo incluye
- ✅ **Aislamiento completo** - No interfiere con el sistema
- ✅ **Reproducible** - Mismo entorno en desarrollo y producción
- ✅ **Fácil actualización** - Solo reconstruyes la imagen
- ✅ **Sin conflictos de dependencias** - Todo está encapsulado

### 📚 Guía Completa

Para instrucciones detalladas paso a paso, consulta la **[Guía de Despliegue con Docker en WHM](./GUIA_DOCKER_WHM.md)**.

**Resumen rápido:**

1. **Instalar Docker y Docker Compose** en CentOS 7
2. **Subir el proyecto** al servidor
3. **Construir la imagen**: `docker-compose build`
4. **Iniciar contenedor**: `docker-compose up -d`
5. **Configurar Apache** como proxy reverso en WHM
6. **Configurar inicio automático** con systemd

**Comandos principales:**

```bash
# Instalar Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Construir y ejecutar
cd ~/algoritmo_ia
docker-compose build
docker-compose up -d

# Ver logs
docker-compose logs -f backend
```

**Ver la guía completa:** [GUIA_DOCKER_WHM.md](./GUIA_DOCKER_WHM.md)

## Opción 1: Railway (Recomendado - Más Fácil)

Railway permite desplegar backend y frontend fácilmente.

### Backend en Railway

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

### Frontend en Railway

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

## Opción 2: Render

### Backend en Render

1. Crear cuenta en [render.com](https://render.com)
2. **New** → **Web Service**
3. Conectar repositorio GitHub
4. Configurar:
   - **Name**: `algoritmo-ia-backend`
   - **Environment**: **Python 3** ⚠️ **Importante**: Selecciona Python 3, NO Docker (a menos que tengas un Dockerfile específico)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT` ⚠️ **CRÍTICO**: Debe ser `uvicorn`, NO `gunicorn`
5. **Environment Variables**:
   ```
   PORT=8000
   ALLOWED_ORIGINS=https://tu-frontend.onrender.com
   ```
6. Render asignará una URL (ej: `https://algoritmo-ia-backend.onrender.com`)

**Notas importantes**:

- **Environment**: Si Render detecta automáticamente Docker, cámbialo a **Python 3**. Docker solo es necesario si tienes un `Dockerfile` en la raíz del proyecto y quieres usarlo.
- **Start Command**: Asegúrate de que sea `uvicorn main:app --host 0.0.0.0 --port $PORT`. Si Render intenta usar `gunicorn`, cámbialo manualmente en la configuración.
- **Procfile**: Si tienes un `Procfile` en tu repositorio, Render puede leerlo. Asegúrate de que contenga `web: uvicorn main:app --host 0.0.0.0 --port $PORT` (sin gunicorn).

### Frontend en Render

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

## Opción 3: Vercel (Frontend) + Railway/Render (Backend)

Esta opción combina Vercel para el frontend (muy rápido y fácil) con Railway o Render para el backend.

### Frontend en Vercel

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

## Opción 4: Docker Compose (VPS/Cloud/Servidor Propio)

### Backend Dockerfile

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
RUN mkdir -p uploads outputs artifacts feedback_data feedback_data/images artifacts/backups

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Frontend Dockerfile

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

### docker-compose.yml

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
      - ./feedback_data:/app/feedback_data # ⚠️ CRÍTICO para reentrenamiento
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

## Configuración de Variables de Entorno en Producción

### Backend

**Railway/Render**:

```env
PORT=8000
ALLOWED_ORIGINS=https://tu-frontend.vercel.app,https://tu-dominio.com
```

**Nota**: En Railway y Render, `PORT` se asigna automáticamente, pero puedes especificarlo.

### Frontend

**Vercel/Railway/Render**:

```env
VITE_API_URL=https://tu-backend.railway.app
```

**Importante**:

- En Vercel, agrega la variable en **Settings → Environment Variables**
- Selecciona todos los ambientes (Production, Preview, Development)
- Vercel reconstruirá automáticamente después de agregar variables

## Incluir el Modelo Entrenado en el Despliegue

⚠️ **PASO CRÍTICO**: Para que la clasificación funcione en producción, el modelo debe estar entrenado e incluido en el repositorio.

**Proceso**:

1. **Entrenar el modelo** (ver README.md - sección de Entrenamiento del Modelo)

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

## ⚠️ Consideraciones Especiales para Reentrenamiento en Producción

El reentrenamiento tiene requisitos específicos que debes considerar al desplegar:

### 1. **Almacenamiento Persistente**

El sistema necesita almacenar:

- `feedback_data/feedback.csv` - Historial de feedback
- `feedback_data/images/` - Imágenes para reentrenamiento
- `artifacts/best_model.pth` - Modelo entrenado
- `artifacts/backups/` - Backups del modelo

**Render/Railway (Gratuito)**:

- ⚠️ **Limitación**: El almacenamiento es efímero. Los datos se pierden al reiniciar el servicio.
- **Solución**: Usa volúmenes persistentes (Railway) o almacenamiento externo (S3, etc.)

**Railway con Volúmenes**:

1. En tu servicio backend → **Settings** → **Volumes**
2. Agregar volúmenes para:
   - `feedback_data/` → `/app/feedback_data`
   - `artifacts/` → `/app/artifacts`
   - `uploads/` → `/app/uploads` (opcional, para mantener imágenes)

**Render (Gratuito)**:

- ⚠️ **NO soporta volúmenes persistentes en el plan gratuito**
- ⚠️ **Los datos se pierden cuando el servicio se reinicia** (sleep después de inactividad, despliegues, etc.)
- **¿Funcionará el reentrenamiento?**
  - ✅ **Sí, PERO con limitaciones**:
    - Funciona mientras el servicio está activo
    - El feedback se guarda en disco temporal (`feedback_data/`)
    - El reentrenamiento puede ejecutarse y actualizar el modelo
    - ⚠️ **PERO**: Si Render reinicia el servicio (sleep, despliegue, error), se pierden:
      - Todos los datos de `feedback_data/` (feedback.csv, imágenes)
      - El modelo actualizado en `artifacts/best_model.pth` (se restaura al del repositorio)
      - Los backups en `artifacts/backups/`
  - **Cuándo se reinicia**:
    - Después de 15 minutos de inactividad (sleep)
    - Al hacer un nuevo despliegue (git push)
    - Si el servicio falla y se reinicia
  - **Alternativas para persistencia**:
    - **Opción 1**: Usar almacenamiento externo (S3, Google Cloud Storage) para feedback y modelos
    - **Opción 2**: Usar Render PostgreSQL para metadatos (pero no las imágenes)
    - **Opción 3**: Plan de pago de Render ($7/mes) que mantiene el servicio activo (menos sleep)
    - **Opción 4**: Reentrenamiento externo (servidor separado que guarda en S3/DB)

### 2. **Recursos Computacionales**

El reentrenamiento requiere:

- **CPU**: Mínimo 2 cores recomendados
- **RAM**: Mínimo 2GB (4GB+ recomendado para datasets grandes)
- **Tiempo**: Puede tomar 10-30 minutos dependiendo del tamaño del dataset

**Render/Railway (Gratuito)**:

- ⚠️ **Limitación**: Recursos limitados, puede ser lento o fallar con datasets grandes
- **Solución**:
  - Usar menos épocas (`--epochs 5` en lugar de 10)
  - Reentrenar solo cuando haya suficientes datos (50+ imágenes)
  - Considerar un plan de pago para más recursos

### 3. **Timeout de Requests**

**Render/Railway**:

- ⚠️ **Limitación**: Requests HTTP tienen timeout (típicamente 30-60 segundos)
- **Solución**: El reentrenamiento se ejecuta en background (threading), pero:
  - El endpoint `/api/v1/model/retrain` retorna inmediatamente
  - Usa `/api/v1/model/retrain/status` para verificar el progreso
  - El frontend hace polling automático cada 2 segundos

### 4. **Recomendaciones por Plataforma**

**Railway (Recomendado para Reentrenamiento)**:

- ✅ Soporta volúmenes persistentes
- ✅ Mejor para procesos largos
- ✅ Más recursos en plan gratuito
- **Configuración**:
  ```yaml
  # railway.json (opcional, para configuración avanzada)
  {
    "build": { "builder": "NIXPACKS" },
    "deploy":
      {
        "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
        "restartPolicyType": "ON_FAILURE",
        "restartPolicyMaxRetries": 10,
      },
  }
  ```

**Render**:

- ⚠️ **Plan gratuito**: Funciona pero **sin persistencia de datos**
  - ✅ El reentrenamiento puede ejecutarse mientras el servicio está activo
  - ✅ Los datos se guardan temporalmente en disco
  - ⚠️ **Problema crítico**: Los datos se pierden cuando:
    - El servicio entra en sleep (después de 15 min de inactividad)
    - Se hace un nuevo despliegue (git push)
    - El servicio se reinicia por error
  - **Recomendación**:
    - Para desarrollo/pruebas: ✅ Funciona bien
    - Para producción: ⚠️ No recomendado sin persistencia
- **Planes de pago**: Render ofrece planes de pago que permiten discos persistentes y más recursos
- **Alternativa sin plan de pago**:
  - Usar almacenamiento externo (S3) para feedback y modelos (ver sección 6)
  - O ejecutar reentrenamiento externamente (cron job en otro servidor)

**VPS/Servidor Propio (Mejor para Reentrenamiento)**:

- ✅ Control total sobre recursos
- ✅ Almacenamiento persistente garantizado
- ✅ Sin límites de tiempo
- ✅ Puedes usar GPU si está disponible
- **Recomendado para**: Producción con mucho tráfico

### 5. **Configuración de Docker para Reentrenamiento**

Si usas Docker, asegúrate de montar volúmenes:

```yaml
# docker-compose.yml
services:
  backend:
    build: .
    volumes:
      - ./feedback_data:/app/feedback_data # ⚠️ CRÍTICO para reentrenamiento
      - ./artifacts:/app/artifacts # ⚠️ CRÍTICO para modelos
      - ./uploads:/app/uploads # Opcional
      - ./outputs:/app/outputs # Opcional
    environment:
      - PORT=8000
```

### 6. **Alternativa: Almacenamiento Externo (S3/Cloud Storage)**

Para Render sin plan de pago, puedes usar almacenamiento externo para mantener los datos:

**Configuración con AWS S3** (ejemplo):

1. **Crear bucket S3** para feedback y modelos
2. **Modificar `feedback_storage.py`** para guardar en S3:

   ```python
   import boto3
   import os

   s3 = boto3.client('s3',
       aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
       aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
   )

   # Guardar feedback.csv en S3 después de cada actualización
   s3.upload_file('feedback_data/feedback.csv', 'bucket-name', 'feedback.csv')

   # Cargar desde S3 al iniciar
   s3.download_file('bucket-name', 'feedback.csv', 'feedback_data/feedback.csv')
   ```

3. **Variables de entorno en Render**:
   ```
   AWS_ACCESS_KEY=tu_key
   AWS_SECRET_KEY=tu_secret
   S3_BUCKET=tu-bucket
   ```
4. **Ventajas**:
   - ✅ Datos persistentes incluso si Render reinicia
   - ✅ Funciona en plan gratuito
   - ✅ Escalable
   - ✅ Backup automático

**Otras opciones de almacenamiento**:

- Google Cloud Storage
- Azure Blob Storage
- DigitalOcean Spaces
- Backblaze B2

### 7. **Alternativa: Reentrenamiento Externo**

Si Render/Railway no es suficiente, puedes:

1. **Backend en Render/Railway** (solo clasificación)
2. **Servidor separado para reentrenamiento**:

   - VPS barato (DigitalOcean $5/mes, Linode, etc.)
   - Google Colab (gratis, con GPU) - ejecutar manualmente
   - AWS EC2 (con GPU si es necesario)

   **Flujo**:

   - Backend guarda feedback en S3 o base de datos
   - Servidor de reentrenamiento lee datos periódicamente (cron job)
   - Reentrena y sube el modelo actualizado a S3
   - Backend descarga el modelo actualizado desde S3 al iniciar

### 8. **Configuración de Variables de Entorno para Reentrenamiento**

```env
# Backend
PORT=8000
ALLOWED_ORIGINS=https://tu-frontend.vercel.app

# Opcional: Configurar límites de reentrenamiento
MAX_RETRAIN_EPOCHS=10
MIN_FEEDBACK_FOR_RETRAIN=10
RETRAIN_TIMEOUT=3600  # 1 hora en segundos
```

## Checklist de Despliegue

- [ ] Backend desplegado y accesible
- [ ] Frontend configurado con `VITE_API_URL` correcta
- [ ] CORS configurado en backend con URL del frontend
- [ ] Modelo entrenado (`artifacts/best_model.pth`) incluido en el despliegue
- [ ] Variables de entorno configuradas
- [ ] **Almacenamiento persistente configurado** (volúmenes o S3) ⚠️ **CRÍTICO para reentrenamiento**
- [ ] Probar subida de imágenes
- [ ] Probar descarga de CSV
- [ ] Verificar que las clasificaciones funcionen
- [ ] **Probar guardado de feedback** (verificar que `feedback_data/feedback.csv` se cree)
- [ ] **Probar reentrenamiento manual** desde el frontend
- [ ] Verificar que el modelo se actualice después del reentrenamiento

## Troubleshooting de Despliegue

### Problemas en Railway/Render

**Error: `gunicorn: command not found`** (Render):

Este error ocurre cuando Render intenta usar `gunicorn` pero no está instalado. **Solución**:

1. **Verifica el Start Command en Render**:

   - Ve a tu servicio en Render → Settings
   - En **Start Command**, debe ser: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **NO debe ser**: `gunicorn` o cualquier comando con gunicorn

2. **Verifica el Procfile** (si existe):

   - Debe contener: `web: uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Si tiene `gunicorn`, cámbialo a `uvicorn`

3. **Si Render detecta automáticamente gunicorn**:
   - Ignora la detección automática
   - Configura manualmente el Start Command como se indica arriba

**Build falla**:

- Verifica que todas las dependencias estén en `requirements.txt`
- Revisa los logs de build en la plataforma
- Asegúrate de usar Python 3.11 o 3.12 (no 3.14+)

**Frontend no encuentra el backend**:

- Usa la URL completa del backend en `VITE_API_URL`
- Reconstruye el frontend después de cambiar variables de entorno

---

**¿Necesitas ayuda?** Consulta el [README.md](./README.md) para información general del proyecto o revisa los logs de la plataforma de despliegue.
