# Базовий образ
FROM python:3.11-slim

# Встановити системні залежності
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Робоча директорія
WORKDIR /app

# Копіюємо requirements та встановлюємо залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо .env файл
COPY .env .

# Копіюємо весь код
COPY . .

# Вивід логів одразу
ENV PYTHONUNBUFFERED=1

# Команда запуску
CMD ["python", "-m", "app.main"] 