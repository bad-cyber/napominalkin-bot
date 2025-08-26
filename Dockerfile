FROM python:3.9-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создаем непривилегированного пользователя для безопасности
RUN useradd -m -u 1000 napominalkin

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы требований сначала для кэширования
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы
COPY --chown=napominalkin:napominalkin . .

# Переключаемся на непривилегированного пользователя
USER napominalkin

# Создаем директорию для данных
RUN mkdir -p /app/data

# Экспортируем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Запускаем бота
CMD ["python", "main.py"]
