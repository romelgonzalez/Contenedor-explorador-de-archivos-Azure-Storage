# Usar una imagen base oficial de Python. La versión 'slim' es más ligera.
FROM python:3.9-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de dependencias primero para aprovechar el caché de Docker
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación al directorio de trabajo
# Esto ahora incluye el archivo app.py y la carpeta 'templates'
COPY . .

# Definir la variable de entorno para la ruta de montaje
ENV MOUNT_PATH /mnt/azure

# Exponer el puerto en el que se ejecutará la aplicación
EXPOSE 8000

# El comando para iniciar la aplicación cuando el contenedor se ejecute
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
