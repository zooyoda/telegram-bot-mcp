# Используем минимальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY pyproject.toml requirements.txt uv.lock ./

# Обновляем pip + poetry (если poetry используется)
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Копируем всё остальное
COPY . .

# Открываем порт (если у FastMCP 8000)
EXPOSE 8000

# Указываем переменные окружения для Python
ENV PYTHONUNBUFFERED=1

# Запускаем сервер
CMD ["uvicorn", "server:main", "--host", "0.0.0.0", "--port", "8000"]
