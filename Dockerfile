# Imagen base con dependencias científicas y de visión
FROM python:3.11-bullseye

# Evita prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias de sistema necesarias para OpenCV, Tesseract y psycopg2
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Exponer puerto Flask
EXPOSE 5000

# Comando de arranque
CMD ["python", "app.py"]
