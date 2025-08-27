# Imagen base
FROM python:3.11-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar tu aplicación
COPY . .

# Exponer el puerto Flask
EXPOSE 5000

# Comando de arranque
CMD ["python", "app.py"]
