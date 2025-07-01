# syntax=docker/dockerfile:1

# Базовый образ
FROM python:3.10-slim

# Установим рабочую директорию
WORKDIR /app

# Скопируем файлы проекта
COPY . .

# Установим зависимости
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Укажем переменные окружения (например, токен бота)
# ENV TELEGRAM_BOT_TOKEN=your_token_here

# Откроем порт (если нужно, например 8080)
EXPOSE 8080

# Запустим сервер
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
