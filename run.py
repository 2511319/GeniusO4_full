#!/usr/bin/env python
# run.py — единый запуск в трёх режимах: dev, docker, prod

import os
import sys
import subprocess
import argparse
from dotenv import load_dotenv

def load_env(mode: str):
    env_file = f".env.{mode}"
    if not os.path.exists(env_file):
        print(f"⚠️  Не найден {env_file}")
        sys.exit(1)
    load_dotenv(env_file, override=True)
    print(f"✔ Загружено окружение из {env_file}")

def main():
    parser = argparse.ArgumentParser(description="Запуск ChartGenius")
    parser.add_argument("--mode", choices=["dev", "docker", "prod"], default="dev")
    args = parser.parse_args()
    mode = args.mode

    load_env(mode)

    # создаём папки логов
    os.makedirs("api/dev_logs", exist_ok=True)
    os.makedirs("ui/dev_logs", exist_ok=True)

    python = sys.executable
    api_port = os.getenv("API_PORT", "8000")
    dash_port = os.getenv("DASH_PORT", "8050")

    if mode == "dev":
        backend_cmd = [
            python, "-m", "uvicorn",
            "app:app",  # запускаем из cwd=api
            "--reload", "--port", api_port
        ]
        frontend_cmd = [python, "app.py"]  # запускаем из cwd=ui

        # старт бекенда
        print("🚀 Backend:", " ".join(backend_cmd))
        p_api = subprocess.Popen(
            backend_cmd,
            cwd=os.path.join(os.getcwd(), "api"),
            env=os.environ.copy()
        )

        # старт фронтенда
        print("🚀 Frontend:", " ".join(frontend_cmd))
        p_ui = subprocess.Popen(
            frontend_cmd,
            cwd=os.path.join(os.getcwd(), "ui"),
            env=os.environ.copy()
        )

        try:
            p_api.wait()
            p_ui.wait()
        except KeyboardInterrupt:
            print("\n🛑 Остановка сервисов...")
            p_api.terminate()
            p_ui.terminate()

    elif mode == "docker":
        os.execvp("docker-compose", ["docker-compose", "up", "--build"])

    else:  # prod
        print("ℹ️  Для продакшена используйте ./deploy.sh")

if __name__ == "__main__":
    main()
