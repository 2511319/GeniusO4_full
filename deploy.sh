#!/usr/bin/env bash
# deploy.sh — сборка образов и деплой в Google Cloud Run

set -e
# 1) подгружаем продовый .env
export $(grep -v '^#' .env.prod | xargs)

# 2) строим и пушим образы
docker build -t gcr.io/$GCP_PROJECT_ID/chartgenius-api:latest -f backend/Dockerfile .
docker build -t gcr.io/$GCP_PROJECT_ID/chartgenius-frontend:latest -f frontend/Dockerfile .
docker build -t gcr.io/$GCP_PROJECT_ID/chartgenius-bot:latest -f bot/Dockerfile .

docker push gcr.io/$GCP_PROJECT_ID/chartgenius-api:latest
docker push gcr.io/$GCP_PROJECT_ID/chartgenius-frontend:latest
docker push gcr.io/$GCP_PROJECT_ID/chartgenius-bot:latest

# 3) деплой API
gcloud run deploy chartgenius-api \
  --image gcr.io/$GCP_PROJECT_ID/chartgenius-api:latest \
  --platform managed \
  --region $GCP_REGION \
  --allow-unauthenticated \
  --set-env-vars "OPENAI_API_KEY=$OPENAI_API_KEY,JWT_SECRET_KEY=$JWT_SECRET_KEY,CRYPTOCOMPARE_API_KEY=$CRYPTOCOMPARE_API_KEY"

# 4) деплой фронтенда (проксирует запросы к API_URL)
gcloud run deploy chartgenius-frontend \
  --image gcr.io/$GCP_PROJECT_ID/chartgenius-frontend:latest \
  --platform managed \
  --region $GCP_REGION \
  --allow-unauthenticated \
  --set-env-vars "API_URL=https://chartgenius-api-${GCP_REGION}-a.run.app"

# 5) деплой бота
gcloud run deploy chartgenius-bot \
  --image gcr.io/$GCP_PROJECT_ID/chartgenius-bot:latest \
  --platform managed \
  --region $GCP_REGION \
  --no-allow-unauthenticated \
  --set-env-vars "TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN,ADMIN_TELEGRAM_ID=299820674" \
  --min-instances 1 \
  --max-instances 1
