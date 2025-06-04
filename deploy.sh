#!/usr/bin/env bash
# deploy.sh — сборка образов и деплой в Google Cloud Run

set -e
# 1) подгружаем продовый .env
export $(grep -v '^#' .env.prod | xargs)

# 2) строим и пушим образы
docker build -t gcr.io/$GCP_PROJECT_ID/chartgenius-api:latest -f api/Dockerfile .
docker build -t gcr.io/$GCP_PROJECT_ID/chartgenius-ui:latest -f ui/Dockerfile .

docker push gcr.io/$GCP_PROJECT_ID/chartgenius-api:latest
docker push gcr.io/$GCP_PROJECT_ID/chartgenius-ui:latest

# 3) деплой API
gcloud run deploy chartgenius-api \
  --image gcr.io/$GCP_PROJECT_ID/chartgenius-api:latest \
  --platform managed \
  --region $GCP_REGION \
  --allow-unauthenticated \
  --set-env-vars "OPENAI_API_KEY=$OPENAI_API_KEY,JWT_SECRET_KEY=$JWT_SECRET_KEY,CRYPTOCOMPARE_API_KEY=$CRYPTOCOMPARE_API_KEY"

# 4) деплой UI (проксирует запросы к API_URL)
gcloud run deploy chartgenius-ui \
  --image gcr.io/$GCP_PROJECT_ID/chartgenius-ui:latest \
  --platform managed \
  --region $GCP_REGION \
  --allow-unauthenticated \
  --set-env-vars "API_URL=https://chartgenius-api-${GCP_REGION}-a.run.app"
