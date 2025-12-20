#!/bin/bash

# Script de inicio para Render con disco persistente
# Este script crea enlaces simbólicos desde las rutas del código
# hacia el disco persistente montado en /app/data

# Crear directorios en el disco persistente si no existen
mkdir -p /app/data/feedback_data/images/healthy
mkdir -p /app/data/feedback_data/images/sick
mkdir -p /app/data/artifacts/backups
mkdir -p /app/data/uploads
mkdir -p /app/data/outputs

# Crear enlaces simbólicos si no existen
# Esto permite que el código use rutas relativas como siempre
if [ ! -L feedback_data ] && [ ! -d feedback_data ]; then
    ln -s /app/data/feedback_data feedback_data
    echo "✅ Enlace simbólico creado: feedback_data -> /app/data/feedback_data"
fi

if [ ! -L artifacts ] && [ ! -d artifacts ]; then
    # Si artifacts existe como directorio (con el modelo inicial), moverlo primero
    if [ -d artifacts ] && [ ! -L artifacts ]; then
        # Copiar el modelo inicial al disco persistente si existe
        if [ -f artifacts/best_model.pth ]; then
            mkdir -p /app/data/artifacts
            cp artifacts/best_model.pth /app/data/artifacts/
            echo "✅ Modelo inicial copiado al disco persistente"
        fi
        # Mover otros archivos si existen
        if [ "$(ls -A artifacts 2>/dev/null)" ]; then
            cp -r artifacts/* /app/data/artifacts/ 2>/dev/null || true
        fi
    fi
    # Crear enlace simbólico
    ln -s /app/data/artifacts artifacts
    echo "✅ Enlace simbólico creado: artifacts -> /app/data/artifacts"
fi

if [ ! -L uploads ] && [ ! -d uploads ]; then
    ln -s /app/data/uploads uploads
    echo "✅ Enlace simbólico creado: uploads -> /app/data/uploads"
fi

if [ ! -L outputs ] && [ ! -d outputs ]; then
    ln -s /app/data/outputs outputs
    echo "✅ Enlace simbólico creado: outputs -> /app/data/outputs"
fi

# Verificar que los enlaces están correctos
echo "📁 Verificando estructura de directorios..."
ls -la | grep -E "feedback_data|artifacts|uploads|outputs"

# Iniciar la aplicación
echo "🚀 Iniciando aplicación..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2
