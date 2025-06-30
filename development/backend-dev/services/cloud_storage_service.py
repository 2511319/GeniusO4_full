# 🗄️ Cloud Storage Service for ChartGenius
# Версия: 1.1.0-dev
# Управление промптами в Google Cloud Storage

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from google.cloud import storage
from google.cloud import firestore
import redis.asyncio as redis
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class PromptType(Enum):
    """Типы промптов для анализа"""
    TECHNICAL_ANALYSIS = "technical_analysis"
    FUNDAMENTAL_ANALYSIS = "fundamental_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    RISK_ASSESSMENT = "risk_assessment"

@dataclass
class PromptVersion:
    """Версия промпта"""
    version: str
    created_at: datetime
    created_by: str
    description: str
    file_path: str
    file_size: int
    parameters: Dict[str, Any]

@dataclass
class PromptMetadata:
    """Метаданные промпта"""
    prompt_type: str
    active_version: str
    versions: Dict[str, PromptVersion]
    updated_at: datetime
    updated_by: str

class CloudStorageService:
    """
    Сервис для управления промптами в Google Cloud Storage
    """
    
    def __init__(self):
        self.bucket_name = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET", "chartgenius-prompts")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.cache_ttl = 3600  # 1 час кэширования
        
        # Инициализация клиентов
        try:
            self.storage_client = storage.Client()
            self.bucket = self.storage_client.bucket(self.bucket_name)
            self.db = firestore.Client()
            logger.info(f"Cloud Storage Service инициализирован для bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Ошибка инициализации Cloud Storage Service: {e}")
            raise
    
    async def get_redis(self) -> redis.Redis:
        """Получение Redis клиента"""
        return redis.from_url(self.redis_url)
    
    async def upload_prompt(self, prompt_type: str, version: str, content: str, 
                          description: str = "", parameters: Dict[str, Any] = None,
                          created_by: str = "admin") -> bool:
        """
        Загрузка нового промпта в Cloud Storage
        
        Args:
            prompt_type: Тип промпта (technical_analysis, etc.)
            version: Версия промпта (например, "1.1")
            content: Содержимое промпта
            description: Описание промпта
            parameters: Параметры для LLM (temperature, max_tokens, etc.)
            created_by: Кто создал промпт
            
        Returns:
            bool: Успешность операции
        """
        try:
            if not content.strip():
                raise ValueError("Содержимое промпта не может быть пустым")
            
            if parameters is None:
                parameters = {
                    "temperature": 0.7,
                    "max_tokens": 4000
                }
            
            # Путь к файлу в Cloud Storage
            file_path = f"{prompt_type}/v{version}.txt"
            
            # Загружаем файл в Cloud Storage
            blob = self.bucket.blob(file_path)
            blob.upload_from_string(content, content_type='text/plain')
            
            # Создаем версию промпта
            prompt_version = PromptVersion(
                version=version,
                created_at=datetime.utcnow(),
                created_by=created_by,
                description=description,
                file_path=f"gs://{self.bucket_name}/{file_path}",
                file_size=len(content.encode('utf-8')),
                parameters=parameters
            )
            
            # Обновляем метаданные в Firestore
            await self._update_prompt_metadata(prompt_type, prompt_version)
            
            # Очищаем кэш
            await self._clear_prompt_cache(prompt_type)
            
            logger.info(f"Промпт {prompt_type} v{version} успешно загружен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки промпта {prompt_type} v{version}: {e}")
            return False
    
    async def download_prompt(self, prompt_type: str, version: str = None) -> Optional[str]:
        """
        Скачивание промпта из Cloud Storage
        
        Args:
            prompt_type: Тип промпта
            version: Версия промпта (если None, то активная версия)
            
        Returns:
            str: Содержимое промпта или None
        """
        try:
            # Если версия не указана, получаем активную
            if version is None:
                metadata = await self._get_prompt_metadata(prompt_type)
                if not metadata:
                    return None
                version = metadata.active_version
            
            # Проверяем кэш
            cache_key = f"prompt:{prompt_type}:v{version}"
            redis_client = await self.get_redis()
            cached_content = await redis_client.get(cache_key)
            
            if cached_content:
                logger.debug(f"Промпт {prompt_type} v{version} получен из кэша")
                return cached_content.decode('utf-8')
            
            # Скачиваем из Cloud Storage
            file_path = f"{prompt_type}/v{version}.txt"
            blob = self.bucket.blob(file_path)
            
            if not blob.exists():
                logger.warning(f"Промпт {prompt_type} v{version} не найден")
                return None
            
            content = blob.download_as_text()
            
            # Кэшируем результат
            await redis_client.setex(cache_key, self.cache_ttl, content)
            
            logger.debug(f"Промпт {prompt_type} v{version} загружен из Cloud Storage")
            return content
            
        except Exception as e:
            logger.error(f"Ошибка скачивания промпта {prompt_type} v{version}: {e}")
            return None
    
    async def get_active_prompt(self, prompt_type: str) -> Optional[str]:
        """
        Получение активного промпта
        
        Args:
            prompt_type: Тип промпта
            
        Returns:
            str: Содержимое активного промпта
        """
        return await self.download_prompt(prompt_type)
    
    async def list_prompt_versions(self, prompt_type: str) -> List[str]:
        """
        Получение списка версий промпта
        
        Args:
            prompt_type: Тип промпта
            
        Returns:
            List[str]: Список версий
        """
        try:
            metadata = await self._get_prompt_metadata(prompt_type)
            if not metadata:
                return []
            
            return list(metadata.versions.keys())
            
        except Exception as e:
            logger.error(f"Ошибка получения версий промпта {prompt_type}: {e}")
            return []
    
    async def set_active_version(self, prompt_type: str, version: str, 
                               updated_by: str = "admin") -> bool:
        """
        Установка активной версии промпта
        
        Args:
            prompt_type: Тип промпта
            version: Версия для активации
            updated_by: Кто обновил
            
        Returns:
            bool: Успешность операции
        """
        try:
            metadata = await self._get_prompt_metadata(prompt_type)
            if not metadata:
                logger.error(f"Метаданные промпта {prompt_type} не найдены")
                return False
            
            if version not in metadata.versions:
                logger.error(f"Версия {version} промпта {prompt_type} не существует")
                return False
            
            # Обновляем активную версию
            metadata.active_version = version
            metadata.updated_at = datetime.utcnow()
            metadata.updated_by = updated_by
            
            # Сохраняем в Firestore
            doc_ref = self.db.collection('prompt_metadata').document(prompt_type)
            doc_ref.set(asdict(metadata))
            
            # Очищаем кэш
            await self._clear_prompt_cache(prompt_type)
            
            logger.info(f"Активная версия промпта {prompt_type} установлена на {version}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка установки активной версии {prompt_type}: {e}")
            return False
    
    async def delete_prompt_version(self, prompt_type: str, version: str) -> bool:
        """
        Удаление версии промпта
        
        Args:
            prompt_type: Тип промпта
            version: Версия для удаления
            
        Returns:
            bool: Успешность операции
        """
        try:
            metadata = await self._get_prompt_metadata(prompt_type)
            if not metadata:
                return False
            
            if version not in metadata.versions:
                logger.warning(f"Версия {version} промпта {prompt_type} не существует")
                return True
            
            # Нельзя удалить активную версию
            if metadata.active_version == version:
                logger.error(f"Нельзя удалить активную версию {version} промпта {prompt_type}")
                return False
            
            # Удаляем файл из Cloud Storage
            file_path = f"{prompt_type}/v{version}.txt"
            blob = self.bucket.blob(file_path)
            if blob.exists():
                blob.delete()
            
            # Удаляем из метаданных
            del metadata.versions[version]
            metadata.updated_at = datetime.utcnow()
            
            # Сохраняем в Firestore
            doc_ref = self.db.collection('prompt_metadata').document(prompt_type)
            doc_ref.set(asdict(metadata))
            
            # Очищаем кэш
            await self._clear_prompt_cache(prompt_type, version)
            
            logger.info(f"Версия {version} промпта {prompt_type} удалена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления версии {version} промпта {prompt_type}: {e}")
            return False
    
    async def get_prompt_metadata(self, prompt_type: str) -> Optional[Dict[str, Any]]:
        """
        Получение метаданных промпта для API
        
        Args:
            prompt_type: Тип промпта
            
        Returns:
            Dict: Метаданные промпта
        """
        try:
            metadata = await self._get_prompt_metadata(prompt_type)
            if not metadata:
                return None
            
            # Конвертируем в словарь для API
            result = asdict(metadata)
            
            # Конвертируем datetime в строки
            result['updated_at'] = metadata.updated_at.isoformat()
            for version_key, version_data in result['versions'].items():
                if isinstance(version_data, dict) and 'created_at' in version_data:
                    version_data['created_at'] = version_data['created_at'].isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка получения метаданных промпта {prompt_type}: {e}")
            return None
    
    async def _get_prompt_metadata(self, prompt_type: str) -> Optional[PromptMetadata]:
        """Получение метаданных промпта из Firestore"""
        try:
            doc_ref = self.db.collection('prompt_metadata').document(prompt_type)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            data = doc.to_dict()
            
            # Конвертируем обратно в объекты
            versions = {}
            for version_key, version_data in data.get('versions', {}).items():
                if isinstance(version_data['created_at'], str):
                    version_data['created_at'] = datetime.fromisoformat(version_data['created_at'])
                versions[version_key] = PromptVersion(**version_data)
            
            if isinstance(data['updated_at'], str):
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])
            
            return PromptMetadata(
                prompt_type=data['prompt_type'],
                active_version=data['active_version'],
                versions=versions,
                updated_at=data['updated_at'],
                updated_by=data['updated_by']
            )
            
        except Exception as e:
            logger.error(f"Ошибка получения метаданных из Firestore: {e}")
            return None
    
    async def _update_prompt_metadata(self, prompt_type: str, prompt_version: PromptVersion):
        """Обновление метаданных промпта в Firestore"""
        try:
            # Получаем существующие метаданные
            metadata = await self._get_prompt_metadata(prompt_type)
            
            if metadata is None:
                # Создаем новые метаданные
                metadata = PromptMetadata(
                    prompt_type=prompt_type,
                    active_version=prompt_version.version,
                    versions={prompt_version.version: prompt_version},
                    updated_at=datetime.utcnow(),
                    updated_by=prompt_version.created_by
                )
            else:
                # Обновляем существующие
                metadata.versions[prompt_version.version] = prompt_version
                metadata.updated_at = datetime.utcnow()
                metadata.updated_by = prompt_version.created_by
            
            # Сохраняем в Firestore
            doc_ref = self.db.collection('prompt_metadata').document(prompt_type)
            doc_ref.set(asdict(metadata))
            
        except Exception as e:
            logger.error(f"Ошибка обновления метаданных: {e}")
            raise
    
    async def _clear_prompt_cache(self, prompt_type: str, version: str = None):
        """Очистка кэша промптов"""
        try:
            redis_client = await self.get_redis()
            
            if version:
                # Очищаем конкретную версию
                cache_key = f"prompt:{prompt_type}:v{version}"
                await redis_client.delete(cache_key)
            else:
                # Очищаем все версии
                pattern = f"prompt:{prompt_type}:*"
                keys = await redis_client.keys(pattern)
                if keys:
                    await redis_client.delete(*keys)
            
        except Exception as e:
            logger.error(f"Ошибка очистки кэша: {e}")

# Глобальный экземпляр сервиса
cloud_storage_service = CloudStorageService()
