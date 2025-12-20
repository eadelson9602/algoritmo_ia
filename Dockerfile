FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Actualizar pip, setuptools y wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar PyTorch CPU (más ligero para servidores sin GPU)
# Si necesitas GPU, cambia a: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copiar código
COPY . .

# Crear directorios necesarios con permisos correctos
RUN mkdir -p uploads outputs artifacts feedback_data feedback_data/images artifacts/backups && \
    chmod -R 755 uploads outputs artifacts feedback_data

# Exponer puerto
EXPOSE 8000

# Variables de entorno por defecto
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
