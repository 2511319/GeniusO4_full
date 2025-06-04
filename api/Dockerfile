# api/Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ /app/api
COPY .env.docker /app/.env

ENV PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
