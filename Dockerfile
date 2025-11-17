# Dockerfile
FROM python:3.11-slim
WORKDIR /code

# Instala las nuevas dependencias (incluyendo flask y gunicorn)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de la app
COPY ./app /code/app
EXPOSE 8080


# Usa gunicorn para iniciar el objeto 'app' desde el archivo 'app.main'
# Escucha en el puerto 8080 (igual que antes)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app.main:app"]