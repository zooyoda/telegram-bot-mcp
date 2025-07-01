FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml requirements.txt uv.lock ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "server:main", "--host", "0.0.0.0", "--port", "8000"]
