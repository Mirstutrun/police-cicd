# Образ приложения: Python + зависимости + код
FROM python:3.12-slim

# не создавать .pyc и сразу выводить логи
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# сначала только зависимости: этот слой кэшируется, пока requirements.txt не изменится
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# приложение работает не от root
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 5000
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "app:app"]