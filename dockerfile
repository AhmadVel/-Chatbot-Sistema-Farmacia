# Usa una imagen base oficial de Python
FROM python:3.11.4-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala Tesseract OCR y las dependencias necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-spa \  
    && rm -rf /var/lib/apt/lists/*

# Copia el archivo de requerimientos (requirements.txt) al contenedor
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de la aplicación al contenedor
COPY . .

# Expone el puerto en el que la aplicación escuchará
EXPOSE 5000

# Define el comando de inicio para la aplicación
CMD ["python", "app.py"]