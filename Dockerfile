FROM python:3.11-slim

# Gerekli paketleri kur
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        postgresql-client \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizinini ayarla
WORKDIR /app

# Bağımlılıkları kopyala ve kur
COPY requirements.txt .
RUN pip install -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# Uygulama portunu aç
EXPOSE 8000

# Daphne ile çalıştır
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "CineSocial.asgi:application"] 