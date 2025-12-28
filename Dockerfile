# Usar una imagen base oficial de Python
FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app/src/app.py
ENV FLASK_RUN_PORT=5048

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (ffmpeg es crucial)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app/ ./app/

# Crear directorios para uploads y processed si no existen (aunque se copian, es bueno asegurar permisos)
RUN mkdir -p app/uploads app/processed

# Exponer el puerto 5048
EXPOSE 5048

# Comando para ejecutar la aplicación usando gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5048", "app.src.app:app"]
