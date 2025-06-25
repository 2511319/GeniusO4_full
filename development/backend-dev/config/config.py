# src/config/config.py

import yaml
import os
import logging
from dotenv import load_dotenv
from google.cloud import firestore
import google.auth

# Загрузка переменных окружения из файла .env (если используется)
load_dotenv()

class Config:
    """
    Класс для загрузки и управления конфигурацией приложения.
    Конфигурация загружается из YAML файла и переменных окружения.
    """

    def __init__(self, config_path='configs/config.yaml'):
        # Логгер инициализации
        temp_logger = logging.getLogger('ConfigTemp')
        temp_logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
        if not temp_logger.handlers:
            temp_logger.addHandler(handler)

        # Определяем полный путь к config.yaml
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_full_path = os.path.normpath(os.path.join(script_dir, '..', '..', config_path))

        if not os.path.exists(config_full_path):
            temp_logger.error(f"Файл конфигурации {config_full_path} не найден.")
            self.config = {}
        else:
            try:
                with open(config_full_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
                temp_logger.info(f"Конфигурация загружена из {config_full_path}: {self.config}")
            except yaml.YAMLError as e:
                temp_logger.error(f"Ошибка при разборе YAML файла {config_full_path}: {e}")
                self.config = {}
            except Exception as e:
                temp_logger.error(f"Не удалось загрузить конфигурацию из {config_full_path}: {e}")
                self.config = {}

    def get(self, section: str, key: str, default=None):
        return self.config.get(section, {}).get(key, default)

# Инициализация конфигурации
config = Config()

# Настройка логирования
def setup_logging(config: Config):
    logger = logging.getLogger('ChartGenius2')
    if not logger.hasHandlers():
        LOG_LEVEL = config.get('logging', 'level', 'DEBUG')
        LOG_FORMAT = config.get('logging', 'format',
                                '%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(funcName)s - Line %(lineno)d - %(message)s')
        LOG_FILENAME = config.get('logging', 'filename', 'logs/app.log')

        logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

        formatter = logging.Formatter(LOG_FORMAT)

        handlers = config.get('logging', 'handlers', [])
        if 'console' in handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        if 'file' in handlers:
            log_directory = os.path.dirname(LOG_FILENAME)
            if not os.path.exists(log_directory):
                os.makedirs(log_directory)
                logger.info(f"Директория для логов {log_directory} была создана.")

            file_handler = logging.FileHandler(LOG_FILENAME, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger

logger = setup_logging(config)

# Чтение секретов из переменных окружения
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Проверка наличия ключей
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY не установлен.")
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN не установлен.")

# Другие конфигурации
BINANCE_API_URL = config.get('binance', 'api_url')

DEFAULT_SYMBOL = config.get('app', 'default_symbol', 'BTCUSDT')
DEFAULT_INTERVAL = config.get('app', 'default_interval', '4h')
DEFAULT_DAYS = config.get('app', 'default_days', 15)

# Инициализация Firestore клиента
def get_firestore_client():
    try:
        credentials, project = google.auth.default()
        db = firestore.Client(credentials=credentials, project=project)
        logger.info("Firestore Client успешно инициализирован с использованием default credentials.")
        return db
    except Exception as e:
        logger.error(f"Ошибка инициализации Firestore Client: {e}")
        return None

db = get_firestore_client()
