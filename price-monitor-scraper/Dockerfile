FROM python:3.11-slim

# Instalar dependencias del sistema y Chromium + WebDriver nativos (Debian ARM64/AMD64 compatible)
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    chromium \
    chromium-driver \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Configurar directorio de trabajo
WORKDIR /app

# Copiar dependencias e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente del scraper
COPY . .

# Comando de ejecución por defecto del scraper
CMD ["python", "main.py"]
