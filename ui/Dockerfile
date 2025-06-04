# ui/Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY ui/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ui/ /app/ui
COPY .env.docker /app/.env

ENV PYTHONUNBUFFERED=1

EXPOSE 8050
CMD ["python", "ui/app.py"]
