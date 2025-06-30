#!/usr/bin/env python3
# 🔍 ChartGenius Bot Comprehensive Diagnostics
# Версия: 1.1.0-dev
# Комплексная диагностика deployment pipeline

import asyncio
import aiohttp
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import hashlib

# Конфигурация
PROJECT_ID = "chartgenius-444017"
REGION = "europe-west1"
SERVICE_NAME = "chartgenius-bot"
BOT_TOKEN = "7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0"
ADMIN_USER_ID = "299820674"

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class BotDiagnostics:
    """Комплексная диагностика бота"""
    
    def __init__(self):
        self.session = None
        self.results = {}
        self.errors = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def print_header(self, title: str):
        print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"{Colors.BLUE}{title}{Colors.NC}")
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
    
    def print_success(self, message: str):
        print(f"{Colors.GREEN}✅ {message}{Colors.NC}")
    
    def print_error(self, message: str):
        print(f"{Colors.RED}❌ {message}{Colors.NC}")
        self.errors.append(message)
    
    def print_warning(self, message: str):
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")
    
    def print_info(self, message: str):
        print(f"{Colors.CYAN}ℹ️  {message}{Colors.NC}")
    
    def run_command(self, command: str, capture_output: bool = True) -> tuple:
        """Выполнение shell команды"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=capture_output, 
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timeout"
        except Exception as e:
            return -1, "", str(e)
    
    async def check_local_code_version(self):
        """1. Проверка версии локального кода"""
        self.print_header("1. ПРОВЕРКА ЛОКАЛЬНОГО КОДА")
        
        try:
            # Проверяем существование файла
            bot_file = "bot-dev/bot_aiogram.py"
            if not os.path.exists(bot_file):
                self.print_error(f"Файл {bot_file} не найден")
                return
            
            # Читаем содержимое файла
            with open(bot_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем наличие исправлений
            fixes_check = {
                "send_start_menu function": "async def send_start_menu" in content,
                "AuthMiddleware fallback": "fallback': True" in content,
                "TimeoutError handling": "asyncio.TimeoutError" in content,
                "Error middleware": "error_middleware" in content,
                "Health check": "/health" in content
            }
            
            all_fixes_present = True
            for fix_name, present in fixes_check.items():
                if present:
                    self.print_success(f"Исправление найдено: {fix_name}")
                else:
                    self.print_error(f"Исправление отсутствует: {fix_name}")
                    all_fixes_present = False
            
            # Вычисляем хеш файла
            file_hash = hashlib.md5(content.encode()).hexdigest()
            self.print_info(f"Хеш локального файла: {file_hash}")
            
            self.results['local_code'] = {
                'all_fixes_present': all_fixes_present,
                'file_hash': file_hash,
                'file_size': len(content)
            }
            
        except Exception as e:
            self.print_error(f"Ошибка проверки локального кода: {e}")
    
    async def check_cloud_run_status(self):
        """2. Проверка статуса Cloud Run"""
        self.print_header("2. ПРОВЕРКА CLOUD RUN СТАТУСА")
        
        try:
            # Получаем информацию о сервисе
            cmd = f"gcloud run services describe {SERVICE_NAME} --region={REGION} --format=json"
            returncode, stdout, stderr = self.run_command(cmd)
            
            if returncode != 0:
                self.print_error(f"Не удалось получить информацию о сервисе: {stderr}")
                return
            
            service_info = json.loads(stdout)
            
            # Проверяем статус
            status = service_info.get('status', {})
            conditions = status.get('conditions', [])
            
            for condition in conditions:
                condition_type = condition.get('type')
                condition_status = condition.get('status')
                
                if condition_type == 'Ready':
                    if condition_status == 'True':
                        self.print_success("Сервис готов к работе")
                    else:
                        self.print_error("Сервис не готов к работе")
                        self.print_info(f"Причина: {condition.get('message', 'Неизвестно')}")
            
            # Проверяем URL
            url = status.get('url')
            if url:
                self.print_success(f"URL сервиса: {url}")
                self.results['service_url'] = url
            else:
                self.print_error("URL сервиса не найден")
            
            # Проверяем последнюю ревизию
            latest_revision = status.get('latestReadyRevisionName')
            if latest_revision:
                self.print_info(f"Последняя ревизия: {latest_revision}")
                
                # Получаем детали ревизии
                await self.check_revision_details(latest_revision)
            
            self.results['cloud_run'] = {
                'ready': any(c.get('type') == 'Ready' and c.get('status') == 'True' for c in conditions),
                'url': url,
                'latest_revision': latest_revision
            }
            
        except Exception as e:
            self.print_error(f"Ошибка проверки Cloud Run: {e}")
    
    async def check_revision_details(self, revision_name: str):
        """Проверка деталей ревизии"""
        try:
            cmd = f"gcloud run revisions describe {revision_name} --region={REGION} --format=json"
            returncode, stdout, stderr = self.run_command(cmd)
            
            if returncode != 0:
                self.print_warning(f"Не удалось получить детали ревизии: {stderr}")
                return
            
            revision_info = json.loads(stdout)
            
            # Проверяем образ
            spec = revision_info.get('spec', {})
            containers = spec.get('template', {}).get('spec', {}).get('containers', [])
            
            if containers:
                image = containers[0].get('image')
                self.print_info(f"Используемый образ: {image}")
                
                # Проверяем переменные окружения
                env_vars = containers[0].get('env', [])
                env_dict = {var['name']: var.get('value', 'SECRET') for var in env_vars}
                
                important_vars = ['TELEGRAM_BOT_TOKEN', 'WEBHOOK_URL', 'ENVIRONMENT', 'VERSION']
                for var in important_vars:
                    if var in env_dict:
                        value = env_dict[var] if var != 'TELEGRAM_BOT_TOKEN' else 'HIDDEN'
                        self.print_success(f"Переменная {var}: {value}")
                    else:
                        self.print_warning(f"Переменная {var} не установлена")
            
            # Проверяем время создания
            creation_time = revision_info.get('metadata', {}).get('creationTimestamp')
            if creation_time:
                self.print_info(f"Время создания ревизии: {creation_time}")
                
        except Exception as e:
            self.print_warning(f"Ошибка проверки деталей ревизии: {e}")
    
    async def check_docker_images(self):
        """3. Проверка Docker образов"""
        self.print_header("3. ПРОВЕРКА DOCKER ОБРАЗОВ")
        
        try:
            # Проверяем образы в GCR
            cmd = f"gcloud container images list-tags gcr.io/{PROJECT_ID}/{SERVICE_NAME} --limit=5 --format=json"
            returncode, stdout, stderr = self.run_command(cmd)
            
            if returncode != 0:
                self.print_error(f"Не удалось получить список образов: {stderr}")
                return
            
            images = json.loads(stdout)
            
            if not images:
                self.print_error("Образы не найдены в Container Registry")
                return
            
            self.print_success(f"Найдено {len(images)} образов в GCR")
            
            for i, image in enumerate(images):
                digest = image.get('digest')
                timestamp = image.get('timestamp', {}).get('datetime')
                tags = image.get('tags', [])
                
                self.print_info(f"Образ {i+1}:")
                self.print_info(f"  Digest: {digest}")
                self.print_info(f"  Время: {timestamp}")
                self.print_info(f"  Теги: {', '.join(tags) if tags else 'Нет тегов'}")
            
            # Проверяем локальные образы
            cmd = f"docker images gcr.io/{PROJECT_ID}/{SERVICE_NAME}"
            returncode, stdout, stderr = self.run_command(cmd)
            
            if returncode == 0 and stdout.strip():
                self.print_success("Локальные образы найдены")
                self.print_info(f"Локальные образы:\n{stdout}")
            else:
                self.print_warning("Локальные образы не найдены")
            
            self.results['docker_images'] = {
                'gcr_images_count': len(images),
                'latest_image_time': images[0].get('timestamp', {}).get('datetime') if images else None
            }
            
        except Exception as e:
            self.print_error(f"Ошибка проверки Docker образов: {e}")
    
    async def check_logs(self):
        """4. Анализ логов"""
        self.print_header("4. АНАЛИЗ ЛОГОВ")
        
        try:
            # Получаем логи Cloud Run
            self.print_info("Получение логов Cloud Run...")
            cmd = f'gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name={SERVICE_NAME}" --limit=20 --format=json --freshness=1h'
            returncode, stdout, stderr = self.run_command(cmd)
            
            if returncode != 0:
                self.print_error(f"Не удалось получить логи: {stderr}")
                return
            
            if not stdout.strip():
                self.print_warning("Логи не найдены")
                return
            
            logs = json.loads(stdout)
            
            if not logs:
                self.print_warning("Пустые логи")
                return
            
            self.print_success(f"Найдено {len(logs)} записей в логах")
            
            # Анализируем логи
            error_count = 0
            warning_count = 0
            startup_found = False
            
            for log_entry in logs:
                severity = log_entry.get('severity', 'INFO')
                text_payload = log_entry.get('textPayload', '')
                timestamp = log_entry.get('timestamp')
                
                if severity == 'ERROR':
                    error_count += 1
                    self.print_error(f"[{timestamp}] {text_payload}")
                elif severity == 'WARNING':
                    warning_count += 1
                    self.print_warning(f"[{timestamp}] {text_payload}")
                
                if 'Bot started' in text_payload or 'startup' in text_payload.lower():
                    startup_found = True
                    self.print_success(f"[{timestamp}] {text_payload}")
            
            self.print_info(f"Статистика логов: {error_count} ошибок, {warning_count} предупреждений")
            
            if not startup_found:
                self.print_warning("Не найдено сообщений о запуске бота")
            
            self.results['logs'] = {
                'total_entries': len(logs),
                'error_count': error_count,
                'warning_count': warning_count,
                'startup_found': startup_found
            }
            
        except Exception as e:
            self.print_error(f"Ошибка анализа логов: {e}")
    
    async def check_telegram_webhook(self):
        """5. Проверка Telegram webhook"""
        self.print_header("5. ПРОВЕРКА TELEGRAM WEBHOOK")
        
        try:
            # Получаем информацию о webhook
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
            async with self.session.get(url) as response:
                if response.status != 200:
                    self.print_error(f"Ошибка API Telegram: {response.status}")
                    return
                
                data = await response.json()
                
                if not data.get('ok'):
                    self.print_error(f"Ошибка Telegram API: {data}")
                    return
                
                webhook_info = data['result']
                
                webhook_url = webhook_info.get('url')
                pending_updates = webhook_info.get('pending_update_count', 0)
                last_error = webhook_info.get('last_error_message')
                last_error_date = webhook_info.get('last_error_date')
                
                if webhook_url:
                    self.print_success(f"Webhook URL установлен: {webhook_url}")
                    
                    # Проверяем доступность webhook URL
                    await self.test_webhook_url(webhook_url)
                else:
                    self.print_error("Webhook URL не установлен")
                
                if pending_updates > 0:
                    self.print_warning(f"Ожидающих обновлений: {pending_updates}")
                else:
                    self.print_success("Нет ожидающих обновлений")
                
                if last_error:
                    error_date = datetime.fromtimestamp(last_error_date) if last_error_date else "Неизвестно"
                    self.print_error(f"Последняя ошибка [{error_date}]: {last_error}")
                else:
                    self.print_success("Нет ошибок webhook")
                
                self.results['telegram_webhook'] = {
                    'url_set': bool(webhook_url),
                    'pending_updates': pending_updates,
                    'has_errors': bool(last_error),
                    'last_error': last_error
                }
                
        except Exception as e:
            self.print_error(f"Ошибка проверки webhook: {e}")
    
    async def test_webhook_url(self, webhook_url: str):
        """Тестирование доступности webhook URL"""
        try:
            # Извлекаем базовый URL
            base_url = webhook_url.replace('/webhook', '')
            
            # Тестируем health check
            health_url = f"{base_url}/health"
            async with self.session.get(health_url, timeout=10) as response:
                if response.status == 200:
                    self.print_success("Health check endpoint доступен")
                else:
                    self.print_warning(f"Health check недоступен: {response.status}")
            
            # Тестируем webhook endpoint
            test_data = {"test": "ping"}
            async with self.session.post(webhook_url, json=test_data, timeout=10) as response:
                if response.status in [200, 400, 405]:  # 400/405 ожидаемы для тестового запроса
                    self.print_success("Webhook endpoint отвечает")
                else:
                    self.print_warning(f"Webhook endpoint проблема: {response.status}")
                    
        except asyncio.TimeoutError:
            self.print_error("Timeout при обращении к webhook URL")
        except Exception as e:
            self.print_error(f"Ошибка тестирования webhook URL: {e}")
    
    async def test_bot_commands(self):
        """6. Тестирование команд бота"""
        self.print_header("6. ТЕСТИРОВАНИЕ КОМАНД БОТА")
        
        try:
            # Тест getMe
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok'):
                        bot_info = data['result']
                        self.print_success(f"Бот активен: @{bot_info['username']}")
                    else:
                        self.print_error(f"Ошибка getMe: {data}")
                else:
                    self.print_error(f"HTTP ошибка getMe: {response.status}")
            
            # Отправляем тестовое сообщение админу
            test_message = f"""
🔍 <b>Диагностический тест</b>

Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Тест отправки сообщения от бота.

Если вы получили это сообщение, значит:
✅ Telegram API работает
✅ Токен бота корректный
✅ Отправка сообщений функционирует

Проверьте работу команды /start
            """
            
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": ADMIN_USER_ID,
                "text": test_message,
                "parse_mode": "HTML"
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('ok'):
                        self.print_success("Тестовое сообщение отправлено админу")
                    else:
                        self.print_error(f"Ошибка отправки: {result}")
                else:
                    self.print_error(f"HTTP ошибка отправки: {response.status}")
                    
        except Exception as e:
            self.print_error(f"Ошибка тестирования команд: {e}")
    
    async def generate_report(self):
        """Генерация итогового отчета"""
        self.print_header("ИТОГОВЫЙ ОТЧЕТ ДИАГНОСТИКИ")
        
        print(f"{Colors.CYAN}Время диагностики: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.NC}")
        print(f"{Colors.CYAN}Проект: {PROJECT_ID}{Colors.NC}")
        print(f"{Colors.CYAN}Сервис: {SERVICE_NAME}{Colors.NC}")
        print()
        
        # Статус компонентов
        components = {
            "Локальный код": self.results.get('local_code', {}).get('all_fixes_present', False),
            "Cloud Run сервис": self.results.get('cloud_run', {}).get('ready', False),
            "Docker образы": self.results.get('docker_images', {}).get('gcr_images_count', 0) > 0,
            "Логи системы": self.results.get('logs', {}).get('startup_found', False),
            "Telegram webhook": self.results.get('telegram_webhook', {}).get('url_set', False)
        }
        
        print(f"{Colors.BLUE}СТАТУС КОМПОНЕНТОВ:{Colors.NC}")
        all_ok = True
        for component, status in components.items():
            if status:
                self.print_success(f"{component}")
            else:
                self.print_error(f"{component}")
                all_ok = False
        
        print()
        
        # Рекомендации
        print(f"{Colors.BLUE}РЕКОМЕНДАЦИИ:{Colors.NC}")
        
        if not all_ok:
            if not components["Локальный код"]:
                self.print_warning("Проверьте что все исправления применены в локальном коде")
            
            if not components["Cloud Run сервис"]:
                self.print_warning("Перезапустите деплой в Cloud Run")
            
            if not components["Docker образы"]:
                self.print_warning("Пересоберите и загрузите Docker образ")
            
            if not components["Telegram webhook"]:
                self.print_warning("Настройте Telegram webhook заново")
        else:
            self.print_success("Все компоненты в порядке - проблема может быть в другом")
        
        # Ошибки
        if self.errors:
            print(f"\n{Colors.RED}НАЙДЕННЫЕ ОШИБКИ:{Colors.NC}")
            for i, error in enumerate(self.errors, 1):
                print(f"{Colors.RED}{i}. {error}{Colors.NC}")
        
        return all_ok

async def main():
    """Главная функция диагностики"""
    print(f"{Colors.PURPLE}")
    print("🔍 КОМПЛЕКСНАЯ ДИАГНОСТИКА CHARTGENIUS BOT")
    print("=" * 60)
    print(f"{Colors.NC}")
    
    async with BotDiagnostics() as diagnostics:
        # Выполняем все проверки
        await diagnostics.check_local_code_version()
        await diagnostics.check_cloud_run_status()
        await diagnostics.check_docker_images()
        await diagnostics.check_logs()
        await diagnostics.check_telegram_webhook()
        await diagnostics.test_bot_commands()
        
        # Генерируем отчет
        all_ok = await diagnostics.generate_report()
        
        if all_ok:
            print(f"\n{Colors.GREEN}✅ Диагностика завершена - проблем не обнаружено{Colors.NC}")
            return 0
        else:
            print(f"\n{Colors.RED}❌ Диагностика завершена - обнаружены проблемы{Colors.NC}")
            return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
