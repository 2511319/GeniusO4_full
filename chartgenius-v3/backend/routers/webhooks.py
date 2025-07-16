# backend/routers/webhooks.py
"""
Роутер для обработки webhooks (Telegram, платежи)
"""

import json
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from config.config import get_settings, logger

router = APIRouter()
settings = get_settings()


class TelegramUpdate(BaseModel):
    """Модель Telegram update"""
    update_id: int
    message: Dict[str, Any] = None
    callback_query: Dict[str, Any] = None
    pre_checkout_query: Dict[str, Any] = None
    successful_payment: Dict[str, Any] = None


@router.post("/telegram")
async def telegram_webhook(update: TelegramUpdate):
    """
    Webhook для обработки обновлений Telegram Bot
    """
    try:
        logger.info(f"📱 Получен Telegram update: {update.update_id}")
        
        # Обработка сообщений
        if update.message:
            await _handle_telegram_message(update.message)
        
        # Обработка callback queries
        if update.callback_query:
            await _handle_telegram_callback(update.callback_query)
        
        # Обработка pre-checkout запросов
        if update.pre_checkout_query:
            await _handle_pre_checkout(update.pre_checkout_query)
        
        # Обработка успешных платежей
        if update.successful_payment:
            await _handle_successful_payment(update.successful_payment)
        
        return {"ok": True}
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки Telegram webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка обработки webhook"
        )


@router.post("/telegram-payment")
async def telegram_payment_webhook(request: Request):
    """
    Webhook для обработки платежей Telegram Stars
    """
    try:
        # Получаем raw данные
        body = await request.body()
        data = json.loads(body)
        
        logger.info(f"💳 Получен payment webhook: {data}")
        
        # Проверяем тип события
        if "successful_payment" in data:
            payment_data = data["successful_payment"]
            await _process_telegram_payment(payment_data)
        
        return {"ok": True}
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки payment webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка обработки платежа"
        )


async def _handle_telegram_message(message: Dict[str, Any]):
    """Обработка сообщений Telegram"""
    try:
        user_id = message.get("from", {}).get("id")
        text = message.get("text", "")
        
        logger.info(f"💬 Сообщение от {user_id}: {text}")
        
        # Здесь можно добавить обработку команд бота
        # Например: /start, /help, /analyze и т.д.
        
        if text.startswith("/start"):
            await _handle_start_command(user_id, message)
        elif text.startswith("/help"):
            await _handle_help_command(user_id)
        elif text.startswith("/analyze"):
            await _handle_analyze_command(user_id, text)
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки сообщения: {e}")


async def _handle_telegram_callback(callback_query: Dict[str, Any]):
    """Обработка callback queries"""
    try:
        user_id = callback_query.get("from", {}).get("id")
        data = callback_query.get("data", "")
        
        logger.info(f"🔘 Callback от {user_id}: {data}")
        
        # Обработка различных callback данных
        if data.startswith("subscribe_"):
            plan = data.replace("subscribe_", "")
            await _handle_subscription_callback(user_id, plan)
        elif data == "open_webapp":
            await _handle_webapp_callback(user_id)
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки callback: {e}")


async def _handle_pre_checkout(pre_checkout_query: Dict[str, Any]):
    """Обработка pre-checkout запросов"""
    try:
        query_id = pre_checkout_query.get("id")
        user_id = pre_checkout_query.get("from", {}).get("id")
        currency = pre_checkout_query.get("currency")
        total_amount = pre_checkout_query.get("total_amount")
        
        logger.info(f"💰 Pre-checkout от {user_id}: {total_amount} {currency}")
        
        # Здесь можно добавить валидацию платежа
        # Для демонстрации всегда одобряем
        
        # В реальной реализации здесь будет вызов Bot API:
        # await bot.answer_pre_checkout_query(query_id, ok=True)
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки pre-checkout: {e}")


async def _handle_successful_payment(payment: Dict[str, Any]):
    """Обработка успешных платежей"""
    try:
        user_id = payment.get("from", {}).get("id")
        currency = payment.get("currency")
        total_amount = payment.get("total_amount")
        invoice_payload = payment.get("invoice_payload")
        
        logger.info(f"✅ Успешный платеж от {user_id}: {total_amount} {currency}")
        
        # Активируем подписку
        if invoice_payload:
            try:
                payload_data = json.loads(invoice_payload)
                payment_id = payload_data.get("payment_id")
                
                if payment_id:
                    # Импортируем функцию активации подписки
                    from routers.subscription import _activate_subscription
                    await _activate_subscription(payment_id)
                    
            except json.JSONDecodeError:
                logger.error("❌ Неверный формат invoice_payload")
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки успешного платежа: {e}")


async def _process_telegram_payment(payment_data: Dict[str, Any]):
    """Обработка данных платежа Telegram Stars"""
    try:
        # Извлекаем необходимые данные
        telegram_payment_id = payment_data.get("telegram_payment_charge_id")
        invoice_payload = payment_data.get("invoice_payload")
        
        if not telegram_payment_id or not invoice_payload:
            logger.error("❌ Неполные данные платежа")
            return
        
        # Обновляем статус платежа в базе данных
        from config.database import execute_query
        
        try:
            payload_data = json.loads(invoice_payload)
            payment_id = payload_data.get("payment_id")
            
            if payment_id:
                await execute_query(
                    """UPDATE payments 
                       SET status = 'completed',
                           telegram_payment_id = :telegram_payment_id,
                           completed_at = CURRENT_TIMESTAMP
                       WHERE id = :payment_id""",
                    {
                        "payment_id": payment_id,
                        "telegram_payment_id": telegram_payment_id
                    }
                )
                
                logger.info(f"✅ Платеж {payment_id} обновлен")
                
        except json.JSONDecodeError:
            logger.error("❌ Неверный формат payload")
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки платежа: {e}")


async def _handle_start_command(user_id: int, message: Dict[str, Any]):
    """Обработка команды /start"""
    try:
        # Здесь можно отправить приветственное сообщение
        # и кнопку для открытия WebApp
        
        logger.info(f"👋 Пользователь {user_id} запустил бота")
        
        # В реальной реализации здесь будет отправка сообщения через Bot API
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки /start: {e}")


async def _handle_help_command(user_id: int):
    """Обработка команды /help"""
    try:
        logger.info(f"❓ Пользователь {user_id} запросил помощь")
        
        # Отправка справочной информации
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки /help: {e}")


async def _handle_analyze_command(user_id: int, text: str):
    """Обработка команды /analyze"""
    try:
        logger.info(f"📊 Пользователь {user_id} запросил анализ: {text}")
        
        # Парсинг параметров из команды
        # Например: /analyze BTCUSDT 4h
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки /analyze: {e}")


async def _handle_subscription_callback(user_id: int, plan: str):
    """Обработка callback подписки"""
    try:
        logger.info(f"💎 Пользователь {user_id} выбрал план: {plan}")
        
        # Создание invoice для выбранного плана
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки подписки: {e}")


async def _handle_webapp_callback(user_id: int):
    """Обработка callback открытия WebApp"""
    try:
        logger.info(f"🌐 Пользователь {user_id} открывает WebApp")
        
        # Отправка ссылки на WebApp
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки WebApp: {e}")
