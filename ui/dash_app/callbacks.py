import os
import time
import asyncio
import httpx
from dash import no_update, Input, Output, State

# Флаг для логирования запросов/ответов фронтенда
DEBUG_LOGGING = os.getenv("DEBUG_LOGGING", "false").lower() == "true"
DEV_LOG_DIR = os.path.join(os.getcwd(), "dev_logs")


def ensure_log_dir():
    if DEBUG_LOGGING:
        os.makedirs(DEV_LOG_DIR, exist_ok=True)


def register_callbacks(app):
    @app.callback(
        Output("chart", "figure"),
        Output("analysis", "children"),
        Input("analyze-button", "n_clicks"),
        State("symbol-input", "value"),
        State("interval-dropdown", "value"),
        State("limit-input", "value"),
    )
    def analyze(n_clicks, symbol, interval, limit):
        if not n_clicks:
            return no_update, no_update

        # Запускаем асинхронную функцию запроса
        result = asyncio.run(fetch(symbol, interval, limit))
        if isinstance(result, dict):
            fig = result.get("figure", {})
            analysis_text = result.get("analysis", "")
            return fig, analysis_text
        return no_update, no_update


    async def fetch(symbol: str, interval: str, limit: int) -> dict:
        """
        Отсылает POST /api/analyze без параметра indicators,
        логирует ответ в dev_logs при DEBUG_LOGGING
        """
        ensure_log_dir()

        base_url = os.getenv("API_URL", "http://localhost:8000")
        url = f"{base_url}/api/analyze"
        token = os.getenv("JWT_TOKEN", "")
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "symbol": symbol or "",
            "interval": interval or "",
            "limit": int(limit) if limit else 0,
            # больше не передаём indicators
        }

        async with httpx.AsyncClient() as client:
            try:
                r = await client.post(url, json=payload, headers=headers, timeout=30)

                if DEBUG_LOGGING:
                    ts = int(time.time())
                    log_path = os.path.join(DEV_LOG_DIR, f"frontend_response_{ts}.txt")
                    with open(log_path, "w", encoding="utf-8") as f:
                        f.write(f"URL: {url}\n")
                        f.write(f"Status code: {r.status_code}\n\n")
                        f.write("Response text:\n")
                        f.write(r.text or "<пустое тело>")

                r.raise_for_status()
                return r.json()

            except httpx.HTTPStatusError as http_err:
                print(f"[fetch] HTTP error: {http_err} (status {http_err.response.status_code})")
                print(f"Response text: {http_err.response.text}")

            except ValueError as json_err:
                print(f"[fetch] JSON decode failed: {json_err}")
                print(f"Raw response:\n{r.text}")

            except Exception as err:
                print(f"[fetch] Unexpected error: {err}")

        return {}
