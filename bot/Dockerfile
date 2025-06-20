# bot/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Копируем requirements для бота
COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота и backend (для импортов)
COPY bot/ /app/bot
COPY backend/ /app/backend
COPY configs/ /app/configs
COPY .env.docker /app/.env

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["python", "bot/bot.py"]
