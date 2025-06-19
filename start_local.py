#!/usr/bin/env python3
"""
Скрипт для локального запуска всех сервисов GeniusO4
"""
import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def check_dependencies():
    """Проверяет наличие необходимых зависимостей"""
    print("🔍 Проверка зависимостей...")
    
    # Проверяем Python пакеты для backend
    try:
        import fastapi
        import uvicorn
        import sqlmodel
        print("✅ Backend зависимости установлены")
    except ImportError as e:
        print(f"❌ Отсутствуют backend зависимости: {e}")
        print("Установите: pip install -r backend/requirements.txt")
        return False
    
    # Проверяем Node.js для frontend
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Node.js установлен")
        else:
            print("❌ Node.js не найден")
            return False
    except FileNotFoundError:
        print("❌ Node.js не найден")
        return False
    
    return True

def install_frontend_deps():
    """Устанавливает зависимости frontend"""
    print("📦 Установка зависимостей frontend...")
    try:
        os.chdir('frontend')
        result = subprocess.run(['npm', 'install'], check=True)
        os.chdir('..')
        print("✅ Frontend зависимости установлены")
        return True
    except subprocess.CalledProcessError:
        print("❌ Ошибка установки frontend зависимостей")
        os.chdir('..')
        return False

def start_backend():
    """Запускает backend сервер"""
    print("🚀 Запуск Backend API на http://localhost:8000")
    env = os.environ.copy()
    env['PYTHONPATH'] = str(Path.cwd() / 'backend')
    
    return subprocess.Popen([
        sys.executable, '-m', 'uvicorn', 
        'backend.app:app', 
        '--reload', 
        '--host', '0.0.0.0', 
        '--port', '8000',
        '--env-file', '.env.dev'
    ], env=env)

def start_frontend():
    """Запускает frontend сервер"""
    print("🚀 Запуск Frontend на http://localhost:5173")
    os.chdir('frontend')
    process = subprocess.Popen(['npm', 'run', 'dev'])
    os.chdir('..')
    return process

def start_bot():
    """Запускает Telegram бота"""
    print("🤖 Запуск Telegram Bot...")
    env = os.environ.copy()
    env.update({
        'TELEGRAM_BOT_TOKEN': '7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0',
        'JWT_SECRET_KEY': '34sSDF542rf65EJ1kj',
        'API_URL': 'http://localhost:8000',
        'WEBAPP_URL': 'http://localhost:5173'
    })
    
    return subprocess.Popen([
        sys.executable, 'bot/bot.py'
    ], env=env)

def main():
    """Главная функция"""
    print("🟩 GeniusO4 - Локальный запуск 🟩")
    print("=" * 50)
    
    if not check_dependencies():
        sys.exit(1)
    
    # Устанавливаем frontend зависимости если нужно
    if not Path('frontend/node_modules').exists():
        if not install_frontend_deps():
            sys.exit(1)
    
    processes = []
    
    try:
        # Запускаем backend
        backend_process = start_backend()
        processes.append(('Backend', backend_process))
        time.sleep(3)  # Даем время backend'у запуститься
        
        # Запускаем frontend
        frontend_process = start_frontend()
        processes.append(('Frontend', frontend_process))
        time.sleep(2)
        
        # Запускаем бота
        bot_process = start_bot()
        processes.append(('Bot', bot_process))
        
        print("\n" + "=" * 50)
        print("✅ Все сервисы запущены!")
        print("📊 Frontend: http://localhost:5173")
        print("🔧 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("🤖 Telegram Bot: @Chart_Genius_bot")
        print("\n💡 Нажмите Ctrl+C для остановки всех сервисов")
        print("=" * 50)
        
        # Ждем сигнала остановки
        while True:
            time.sleep(1)
            # Проверяем, что все процессы еще живы
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️  {name} завершился неожиданно")
    
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки...")
    
    finally:
        # Останавливаем все процессы
        print("🔄 Остановка сервисов...")
        for name, process in processes:
            if process.poll() is None:
                print(f"   Остановка {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        print("✅ Все сервисы остановлены")

if __name__ == "__main__":
    main()
