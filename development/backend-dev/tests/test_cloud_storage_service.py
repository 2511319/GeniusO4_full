# 🧪 Tests for Cloud Storage Service
# Версия: 1.1.0-dev
# Тесты для сервиса управления промптами

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from backend.services.cloud_storage_service import CloudStorageService, PromptType


class TestCloudStorageService:
    """Тесты для CloudStorageService"""
    
    @pytest.fixture
    def service(self):
        """Фикстура для создания экземпляра сервиса"""
        with patch('backend.services.cloud_storage_service.storage.Client'), \
             patch('backend.services.cloud_storage_service.firestore.Client'):
            service = CloudStorageService()
            return service
    
    @pytest.fixture
    def mock_bucket(self):
        """Мок для Google Cloud Storage bucket"""
        bucket = Mock()
        blob = Mock()
        bucket.blob.return_value = blob
        return bucket, blob
    
    @pytest.mark.asyncio
    async def test_upload_prompt_success(self, service, mock_bucket):
        """Тест успешной загрузки промпта"""
        bucket, blob = mock_bucket
        service.bucket = bucket
        
        # Мокаем методы
        blob.upload_from_string = Mock()
        service._update_prompt_metadata = AsyncMock()
        service._clear_prompt_cache = AsyncMock()
        
        # Тестируем загрузку
        result = await service.upload_prompt(
            prompt_type="technical_analysis",
            version="1.0",
            content="Test prompt content",
            description="Test description",
            created_by="test_user"
        )
        
        # Проверяем результат
        assert result is True
        blob.upload_from_string.assert_called_once()
        service._update_prompt_metadata.assert_called_once()
        service._clear_prompt_cache.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_upload_prompt_empty_content(self, service):
        """Тест загрузки промпта с пустым содержимым"""
        result = await service.upload_prompt(
            prompt_type="technical_analysis",
            version="1.0",
            content="",
            description="Test description"
        )
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_download_prompt_success(self, service, mock_bucket):
        """Тест успешного скачивания промпта"""
        bucket, blob = mock_bucket
        service.bucket = bucket
        
        # Мокаем Redis
        redis_mock = AsyncMock()
        redis_mock.get.return_value = None
        redis_mock.setex = AsyncMock()
        service.get_redis = AsyncMock(return_value=redis_mock)
        
        # Мокаем метаданные
        service._get_prompt_metadata = AsyncMock(return_value=Mock(active_version="1.0"))
        
        # Мокаем blob
        blob.exists.return_value = True
        blob.download_as_text.return_value = "Test prompt content"
        
        # Тестируем скачивание
        result = await service.download_prompt("technical_analysis", "1.0")
        
        # Проверяем результат
        assert result == "Test prompt content"
        blob.download_as_text.assert_called_once()
        redis_mock.setex.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_download_prompt_from_cache(self, service):
        """Тест получения промпта из кэша"""
        # Мокаем Redis с кэшированным содержимым
        redis_mock = AsyncMock()
        redis_mock.get.return_value = b"Cached prompt content"
        service.get_redis = AsyncMock(return_value=redis_mock)
        
        # Тестируем скачивание
        result = await service.download_prompt("technical_analysis", "1.0")
        
        # Проверяем результат
        assert result == "Cached prompt content"
    
    @pytest.mark.asyncio
    async def test_download_prompt_not_found(self, service, mock_bucket):
        """Тест скачивания несуществующего промпта"""
        bucket, blob = mock_bucket
        service.bucket = bucket
        
        # Мокаем Redis
        redis_mock = AsyncMock()
        redis_mock.get.return_value = None
        service.get_redis = AsyncMock(return_value=redis_mock)
        
        # Мокаем метаданные
        service._get_prompt_metadata = AsyncMock(return_value=Mock(active_version="1.0"))
        
        # Мокаем blob как несуществующий
        blob.exists.return_value = False
        
        # Тестируем скачивание
        result = await service.download_prompt("technical_analysis", "1.0")
        
        # Проверяем результат
        assert result is None
    
    @pytest.mark.asyncio
    async def test_set_active_version_success(self, service):
        """Тест успешной установки активной версии"""
        # Мокаем метаданные
        mock_metadata = Mock()
        mock_metadata.versions = {"1.0": Mock(), "1.1": Mock()}
        mock_metadata.active_version = "1.0"
        
        service._get_prompt_metadata = AsyncMock(return_value=mock_metadata)
        service._clear_prompt_cache = AsyncMock()
        
        # Мокаем Firestore
        doc_ref = Mock()
        service.db.collection.return_value.document.return_value = doc_ref
        
        # Тестируем установку активной версии
        result = await service.set_active_version("technical_analysis", "1.1", "admin")
        
        # Проверяем результат
        assert result is True
        assert mock_metadata.active_version == "1.1"
        doc_ref.set.assert_called_once()
        service._clear_prompt_cache.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_active_version_not_exists(self, service):
        """Тест установки несуществующей версии"""
        # Мокаем метаданные
        mock_metadata = Mock()
        mock_metadata.versions = {"1.0": Mock()}
        
        service._get_prompt_metadata = AsyncMock(return_value=mock_metadata)
        
        # Тестируем установку несуществующей версии
        result = await service.set_active_version("technical_analysis", "2.0", "admin")
        
        # Проверяем результат
        assert result is False
    
    @pytest.mark.asyncio
    async def test_delete_prompt_version_success(self, service, mock_bucket):
        """Тест успешного удаления версии промпта"""
        bucket, blob = mock_bucket
        service.bucket = bucket
        
        # Мокаем метаданные
        mock_metadata = Mock()
        mock_metadata.versions = {"1.0": Mock(), "1.1": Mock()}
        mock_metadata.active_version = "1.0"
        
        service._get_prompt_metadata = AsyncMock(return_value=mock_metadata)
        service._clear_prompt_cache = AsyncMock()
        
        # Мокаем Firestore
        doc_ref = Mock()
        service.db.collection.return_value.document.return_value = doc_ref
        
        # Мокаем blob
        blob.exists.return_value = True
        blob.delete = Mock()
        
        # Тестируем удаление версии
        result = await service.delete_prompt_version("technical_analysis", "1.1")
        
        # Проверяем результат
        assert result is True
        assert "1.1" not in mock_metadata.versions
        blob.delete.assert_called_once()
        doc_ref.set.assert_called_once()
        service._clear_prompt_cache.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_active_version_fails(self, service):
        """Тест попытки удаления активной версии"""
        # Мокаем метаданные
        mock_metadata = Mock()
        mock_metadata.versions = {"1.0": Mock(), "1.1": Mock()}
        mock_metadata.active_version = "1.0"
        
        service._get_prompt_metadata = AsyncMock(return_value=mock_metadata)
        
        # Тестируем удаление активной версии
        result = await service.delete_prompt_version("technical_analysis", "1.0")
        
        # Проверяем результат
        assert result is False
    
    @pytest.mark.asyncio
    async def test_list_prompt_versions(self, service):
        """Тест получения списка версий промпта"""
        # Мокаем метаданные
        mock_metadata = Mock()
        mock_metadata.versions = {"1.0": Mock(), "1.1": Mock(), "1.2": Mock()}
        
        service._get_prompt_metadata = AsyncMock(return_value=mock_metadata)
        
        # Тестируем получение списка версий
        result = await service.list_prompt_versions("technical_analysis")
        
        # Проверяем результат
        assert result == ["1.0", "1.1", "1.2"]
    
    @pytest.mark.asyncio
    async def test_list_prompt_versions_no_metadata(self, service):
        """Тест получения списка версий для несуществующего промпта"""
        service._get_prompt_metadata = AsyncMock(return_value=None)
        
        # Тестируем получение списка версий
        result = await service.list_prompt_versions("nonexistent")
        
        # Проверяем результат
        assert result == []
    
    def test_prompt_type_enum(self):
        """Тест enum типов промптов"""
        assert PromptType.TECHNICAL_ANALYSIS.value == "technical_analysis"
        assert PromptType.FUNDAMENTAL_ANALYSIS.value == "fundamental_analysis"
        assert PromptType.SENTIMENT_ANALYSIS.value == "sentiment_analysis"
        assert PromptType.RISK_ASSESSMENT.value == "risk_assessment"


# Интеграционные тесты
class TestCloudStorageServiceIntegration:
    """Интеграционные тесты для CloudStorageService"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_prompt_lifecycle(self):
        """Тест полного жизненного цикла промпта"""
        # Этот тест требует реальных Google Cloud credentials
        # и должен запускаться только в интеграционной среде
        pytest.skip("Requires real Google Cloud credentials")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_redis_integration(self):
        """Тест интеграции с Redis"""
        # Этот тест требует запущенного Redis
        pytest.skip("Requires running Redis instance")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
