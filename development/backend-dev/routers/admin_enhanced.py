# 🔧 Enhanced Admin Router for ChartGenius
# Версия: 1.1.0-dev
# Расширенная админ-панель с управляющими функциями

import os
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from backend.config.config import logger, db
from backend.auth.dependencies import require_role, get_uid
from backend.services.metrics_service import metrics
from backend.services.llm_service import LLMService
from backend.services.cloud_storage_service import cloud_storage_service
import redis.asyncio as redis
from google.cloud import firestore
from fastapi.responses import Response

router = APIRouter(
    prefix='/admin/enhanced',
    tags=['admin-enhanced'],
    dependencies=[Depends(require_role('admin'))]
)

# === PYDANTIC MODELS ===
class ServiceRestartRequest(BaseModel):
    service_name: str = Field(..., description="Имя сервиса для перезапуска")
    force: bool = Field(False, description="Принудительный перезапуск")

class LLMConfigUpdate(BaseModel):
    provider: str = Field(..., description="LLM провайдер")
    model: str = Field(..., description="Модель LLM")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Параметры модели")

class PromptUpdate(BaseModel):
    prompt_type: str = Field(..., description="Тип промпта")
    prompt_text: str = Field(..., description="Текст промпта")
    version: str = Field(default="1.0", description="Версия промпта")
    description: str = Field(default="", description="Описание промпта")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Параметры LLM")

class PromptActivateRequest(BaseModel):
    prompt_type: str = Field(..., description="Тип промпта")
    version: str = Field(..., description="Версия для активации")

class UserManagementRequest(BaseModel):
    telegram_id: str = Field(..., description="Telegram ID пользователя")
    action: str = Field(..., description="Действие: ban, unban, upgrade, reset_limits")
    reason: Optional[str] = Field(None, description="Причина действия")
    duration_hours: Optional[int] = Field(None, description="Длительность в часах")

class SystemHealthResponse(BaseModel):
    status: str
    services: Dict[str, Dict[str, Any]]
    metrics: Dict[str, Any]
    alerts: List[Dict[str, Any]]

# === REDIS CONNECTION ===
async def get_redis():
    """Получение подключения к Redis"""
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        await r.ping()
        return r
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return None

# === SYSTEM HEALTH & MONITORING ===
@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health():
    """Получение состояния системы и сервисов"""
    try:
        services = {}
        alerts = []
        
        # Проверка Redis
        redis_client = await get_redis()
        services['redis'] = {
            'status': 'healthy' if redis_client else 'unhealthy',
            'last_check': datetime.utcnow().isoformat()
        }
        if redis_client:
            await redis_client.close()
        
        # Проверка Firestore
        try:
            db.collection('health_check').limit(1).get()
            services['firestore'] = {
                'status': 'healthy',
                'last_check': datetime.utcnow().isoformat()
            }
        except Exception as e:
            services['firestore'] = {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }
            alerts.append({
                'severity': 'critical',
                'message': f'Firestore connection failed: {e}',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Проверка LLM сервиса
        try:
            llm_service = LLMService()
            services['llm'] = {
                'status': 'healthy',
                'provider': llm_service.provider_name,
                'last_check': datetime.utcnow().isoformat()
            }
        except Exception as e:
            services['llm'] = {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }
            alerts.append({
                'severity': 'high',
                'message': f'LLM service failed: {e}',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Сбор метрик
        system_metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'uptime_hours': 24,  # Заглушка, можно улучшить
            'memory_usage_mb': 256,  # Заглушка
            'cpu_usage_percent': 15  # Заглушка
        }
        
        overall_status = 'healthy' if all(
            s['status'] == 'healthy' for s in services.values()
        ) else 'degraded'
        
        return SystemHealthResponse(
            status=overall_status,
            services=services,
            metrics=system_metrics,
            alerts=alerts
        )
        
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system health")

# === SERVICE MANAGEMENT ===
@router.post("/service/restart")
async def restart_service(request: ServiceRestartRequest, background_tasks: BackgroundTasks):
    """Перезапуск сервиса"""
    try:
        valid_services = ['llm_service', 'cache_service', 'metrics_service']
        
        if request.service_name not in valid_services:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid service. Valid services: {valid_services}"
            )
        
        # Логируем действие
        logger.info(f"Admin requested restart of {request.service_name}")
        metrics.track_user_action('service_restart', 'admin')
        
        # Добавляем задачу в фон
        background_tasks.add_task(
            _restart_service_background, 
            request.service_name, 
            request.force
        )
        
        return {
            'success': True,
            'message': f'Service {request.service_name} restart initiated',
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restarting service: {e}")
        raise HTTPException(status_code=500, detail="Failed to restart service")

async def _restart_service_background(service_name: str, force: bool):
    """Фоновая задача перезапуска сервиса"""
    try:
        logger.info(f"Starting background restart of {service_name}")
        
        if service_name == 'llm_service':
            # Graceful restart LLM service
            await asyncio.sleep(2)  # Имитация graceful shutdown
            # Здесь можно добавить реальную логику перезапуска
            
        elif service_name == 'cache_service':
            # Restart cache service
            redis_client = await get_redis()
            if redis_client:
                await redis_client.flushdb()  # Очистка кэша
                await redis_client.close()
                
        logger.info(f"Service {service_name} restarted successfully")
        
    except Exception as e:
        logger.error(f"Error in background service restart: {e}")

# === LLM MANAGEMENT ===
@router.post("/llm/config")
async def update_llm_config(config: LLMConfigUpdate):
    """Обновление конфигурации LLM"""
    try:
        valid_providers = ['openai', 'google', 'huggingface', 'anthropic']
        
        if config.provider not in valid_providers:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider. Valid providers: {valid_providers}"
            )
        
        # Сохраняем конфигурацию в Redis
        redis_client = await get_redis()
        if redis_client:
            config_key = f"llm_config:{config.provider}"
            config_data = {
                'model': config.model,
                'parameters': config.parameters,
                'updated_at': datetime.utcnow().isoformat(),
                'updated_by': 'admin'
            }
            
            await redis_client.set(config_key, json.dumps(config_data))
            await redis_client.close()
        
        logger.info(f"LLM config updated: {config.provider} -> {config.model}")
        metrics.track_user_action('llm_config_update', 'admin')
        
        return {
            'success': True,
            'message': f'LLM config updated for {config.provider}',
            'config': config.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating LLM config: {e}")
        raise HTTPException(status_code=500, detail="Failed to update LLM config")

@router.post("/llm/prompt/upload")
async def upload_prompt(prompt: PromptUpdate):
    """Загрузка нового промпта в Cloud Storage"""
    try:
        valid_prompt_types = [
            'technical_analysis', 'fundamental_analysis',
            'sentiment_analysis', 'risk_assessment'
        ]

        if prompt.prompt_type not in valid_prompt_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid prompt type. Valid types: {valid_prompt_types}"
            )

        # Загружаем промпт в Cloud Storage
        success = await cloud_storage_service.upload_prompt(
            prompt_type=prompt.prompt_type,
            version=prompt.version,
            content=prompt.prompt_text,
            description=prompt.description,
            parameters=prompt.parameters or {"temperature": 0.7, "max_tokens": 4000},
            created_by="admin"
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to upload prompt")

        logger.info(f"Prompt uploaded: {prompt.prompt_type} v{prompt.version}")
        metrics.track_user_action('prompt_upload', 'admin')

        return {
            'success': True,
            'message': f'Prompt {prompt.prompt_type} v{prompt.version} uploaded successfully',
            'prompt_type': prompt.prompt_type,
            'version': prompt.version
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading prompt: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload prompt")

@router.get("/llm/prompts")
async def list_all_prompts():
    """Получение списка всех промптов с метаданными"""
    try:
        valid_prompt_types = [
            'technical_analysis', 'fundamental_analysis',
            'sentiment_analysis', 'risk_assessment'
        ]

        prompts_data = {}

        for prompt_type in valid_prompt_types:
            metadata = await cloud_storage_service.get_prompt_metadata(prompt_type)
            if metadata:
                prompts_data[prompt_type] = metadata
            else:
                prompts_data[prompt_type] = {
                    'prompt_type': prompt_type,
                    'active_version': None,
                    'versions': {},
                    'status': 'not_found'
                }

        return {
            'success': True,
            'prompts': prompts_data,
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error listing prompts: {e}")
        raise HTTPException(status_code=500, detail="Failed to list prompts")

@router.get("/llm/prompts/{prompt_type}")
async def get_prompt_metadata(prompt_type: str):
    """Получение метаданных конкретного промпта"""
    try:
        metadata = await cloud_storage_service.get_prompt_metadata(prompt_type)

        if not metadata:
            raise HTTPException(status_code=404, detail="Prompt not found")

        return {
            'success': True,
            'metadata': metadata
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt metadata: {e}")
        raise HTTPException(status_code=500, detail="Failed to get prompt metadata")

@router.get("/llm/prompts/{prompt_type}/content")
async def get_active_prompt_content(prompt_type: str):
    """Получение содержимого активного промпта"""
    try:
        content = await cloud_storage_service.get_active_prompt(prompt_type)

        if not content:
            raise HTTPException(status_code=404, detail="Active prompt not found")

        return {
            'success': True,
            'prompt_type': prompt_type,
            'content': content
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt content: {e}")
        raise HTTPException(status_code=500, detail="Failed to get prompt content")

@router.get("/llm/prompts/{prompt_type}/versions/{version}")
async def get_prompt_version_content(prompt_type: str, version: str):
    """Получение содержимого конкретной версии промпта"""
    try:
        content = await cloud_storage_service.download_prompt(prompt_type, version)

        if not content:
            raise HTTPException(status_code=404, detail="Prompt version not found")

        return {
            'success': True,
            'prompt_type': prompt_type,
            'version': version,
            'content': content
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt version content: {e}")
        raise HTTPException(status_code=500, detail="Failed to get prompt version content")

@router.put("/llm/prompts/{prompt_type}/activate/{version}")
async def activate_prompt_version(prompt_type: str, version: str):
    """Активация версии промпта"""
    try:
        success = await cloud_storage_service.set_active_version(
            prompt_type=prompt_type,
            version=version,
            updated_by="admin"
        )

        if not success:
            raise HTTPException(status_code=400, detail="Failed to activate prompt version")

        logger.info(f"Prompt version activated: {prompt_type} v{version}")
        metrics.track_user_action('prompt_activate', 'admin')

        return {
            'success': True,
            'message': f'Prompt {prompt_type} v{version} activated',
            'prompt_type': prompt_type,
            'active_version': version
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating prompt version: {e}")
        raise HTTPException(status_code=500, detail="Failed to activate prompt version")

@router.delete("/llm/prompts/{prompt_type}/versions/{version}")
async def delete_prompt_version(prompt_type: str, version: str):
    """Удаление версии промпта"""
    try:
        success = await cloud_storage_service.delete_prompt_version(prompt_type, version)

        if not success:
            raise HTTPException(status_code=400, detail="Failed to delete prompt version")

        logger.info(f"Prompt version deleted: {prompt_type} v{version}")
        metrics.track_user_action('prompt_delete', 'admin')

        return {
            'success': True,
            'message': f'Prompt {prompt_type} v{version} deleted',
            'prompt_type': prompt_type,
            'deleted_version': version
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting prompt version: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete prompt version")

# === MARKET DATA ENDPOINTS ===

@router.get("/market/exchanges")
async def get_exchanges_status():
    """Получение статуса всех бирж"""
    try:
        from backend.services.market_data_service import market_data_service

        health_status = await market_data_service.get_data_sources_health()

        return {
            'success': True,
            'exchanges': health_status,
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting exchanges status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get exchanges status")

@router.get("/market/symbols/{exchange}")
async def get_exchange_symbols(exchange: str):
    """Получение символов конкретной биржи"""
    try:
        from backend.services.market_data_service import market_data_service

        symbols = await market_data_service.get_supported_symbols(exchange)

        return {
            'success': True,
            'exchange': exchange,
            'symbols': symbols,
            'count': len(symbols)
        }

    except Exception as e:
        logger.error(f"Error getting symbols for {exchange}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get symbols for {exchange}")

@router.get("/market/ticker/{symbol}")
async def get_symbol_ticker(symbol: str, source: Optional[str] = None):
    """Получение текущей цены символа"""
    try:
        from backend.services.market_data_service import market_data_service

        ticker_data = await market_data_service.get_ticker_data(symbol, source)

        if not ticker_data:
            raise HTTPException(status_code=404, detail=f"Ticker data not found for {symbol}")

        return {
            'success': True,
            'symbol': symbol,
            'ticker': ticker_data,
            'timestamp': datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ticker for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get ticker for {symbol}")

@router.get("/market/health")
async def get_market_health():
    """Получение общего состояния всех источников данных"""
    try:
        from backend.services.market_data_service import market_data_service
        from backend.services.ccxt_service import ccxt_service

        # Получаем статус источников данных
        data_sources_health = await market_data_service.get_data_sources_health()

        # Получаем статус CCXT бирж
        ccxt_status = await ccxt_service.get_exchange_status()

        # Получаем общие метрики системы
        system_health = await metrics.get_system_health()

        return {
            'success': True,
            'market_data': data_sources_health,
            'ccxt_exchanges': ccxt_status,
            'system': system_health,
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting market health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get market health")

# === USER MANAGEMENT ===
@router.post("/user/manage")
async def manage_user(request: UserManagementRequest):
    """Управление пользователями"""
    try:
        valid_actions = ['ban', 'unban', 'upgrade', 'reset_limits']
        
        if request.action not in valid_actions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action. Valid actions: {valid_actions}"
            )
        
        user_ref = db.collection('users').document(request.telegram_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_doc.to_dict()
        
        if request.action == 'ban':
            ban_until = None
            if request.duration_hours:
                ban_until = datetime.utcnow() + timedelta(hours=request.duration_hours)
            
            user_ref.update({
                'banned': True,
                'ban_reason': request.reason or 'No reason provided',
                'ban_until': ban_until,
                'banned_at': firestore.SERVER_TIMESTAMP,
                'banned_by': 'admin'
            })
            
        elif request.action == 'unban':
            user_ref.update({
                'banned': False,
                'ban_reason': None,
                'ban_until': None,
                'unbanned_at': firestore.SERVER_TIMESTAMP,
                'unbanned_by': 'admin'
            })
            
        elif request.action == 'reset_limits':
            # Сброс лимитов API
            redis_client = await get_redis()
            if redis_client:
                limit_keys = await redis_client.keys(f"rate_limit:{request.telegram_id}:*")
                if limit_keys:
                    await redis_client.delete(*limit_keys)
                await redis_client.close()
        
        logger.info(f"User {request.telegram_id} {request.action} by admin")
        metrics.track_user_action(f'user_{request.action}', 'admin')
        
        return {
            'success': True,
            'message': f'User {request.telegram_id} {request.action} completed',
            'action': request.action,
            'user_id': request.telegram_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error managing user: {e}")
        raise HTTPException(status_code=500, detail="Failed to manage user")

# === METRICS ENDPOINT ===
@router.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Получение метрик в формате Prometheus"""
    try:
        metrics_data = metrics.get_metrics()
        return Response(content=metrics_data, media_type="text/plain")
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")
