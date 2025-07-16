# backend/routers/subscription.py
"""
Роутер для управления подписками и Telegram Stars payments
"""

import json
from typing import Dict, Any, List
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

from auth.dependencies import get_current_user
from config.config import get_settings, logger, Constants
from config.database import execute_query, execute_one

router = APIRouter()
settings = get_settings()


class SubscriptionPlan(BaseModel):
    """Модель плана подписки"""
    code: str
    name: str
    price_stars: int
    analyses_per_day: int
    description: str


class CreatePaymentRequest(BaseModel):
    """Модель запроса создания платежа"""
    plan_code: str
    payment_method: str = "telegram_stars"


class PaymentResponse(BaseModel):
    """Модель ответа создания платежа"""
    success: bool
    payment_id: int
    amount_stars: int
    telegram_invoice_link: str


class SubscriptionResponse(BaseModel):
    """Модель ответа подписки"""
    success: bool
    subscription: Dict[str, Any]


@router.get("/plans")
async def get_subscription_plans() -> Dict[str, List[SubscriptionPlan]]:
    """
    Получение доступных планов подписки
    """
    try:
        plans = []
        
        for code, info in Constants.SUBSCRIPTION_PLANS.items():
            if code == 'free':
                continue  # Бесплатный план не продается
            
            description = _get_plan_description(code, info)
            
            plans.append(SubscriptionPlan(
                code=code,
                name=info['name'],
                price_stars=info['price'],
                analyses_per_day=info['analyses_per_day'],
                description=description
            ))
        
        return {
            "success": True,
            "plans": plans
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения планов подписки: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения планов"
        )


@router.get("/current")
async def get_current_subscription(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Получение текущей подписки пользователя
    """
    try:
        query = """
            SELECT id, plan_name, status, price_stars, starts_at, 
                   expires_at, auto_renew, created_at
            FROM subscriptions
            WHERE user_id = :user_id AND status = 'active'
            ORDER BY created_at DESC
            FETCH FIRST 1 ROWS ONLY
        """
        
        result = await execute_one(query, {"user_id": current_user['id']})
        
        if result:
            subscription = {
                "id": result[0],
                "plan_name": result[1],
                "status": result[2],
                "price_stars": result[3],
                "starts_at": result[4].isoformat() if result[4] else None,
                "expires_at": result[5].isoformat() if result[5] else None,
                "auto_renew": bool(result[6]),
                "created_at": result[7].isoformat() if result[7] else None
            }
        else:
            # Бесплатная подписка по умолчанию
            subscription = {
                "id": None,
                "plan_name": "free",
                "status": "active",
                "price_stars": 0,
                "starts_at": None,
                "expires_at": None,
                "auto_renew": False,
                "created_at": None
            }
        
        return SubscriptionResponse(
            success=True,
            subscription=subscription
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения подписки: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения подписки"
        )


@router.post("/purchase", response_model=PaymentResponse)
async def create_payment(
    request: CreatePaymentRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Создание платежа для покупки подписки
    """
    try:
        # Проверяем план подписки
        if request.plan_code not in Constants.SUBSCRIPTION_PLANS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный план подписки"
            )
        
        plan_info = Constants.SUBSCRIPTION_PLANS[request.plan_code]
        
        if request.plan_code == 'free':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Бесплатный план не требует покупки"
            )
        
        # Создаем запись платежа
        payment_query = """
            INSERT INTO payments (
                user_id, payment_method, amount_stars, status, metadata
            ) VALUES (
                :user_id, :payment_method, :amount_stars, 'pending', :metadata
            ) RETURNING id
        """
        
        metadata = {
            "plan_code": request.plan_code,
            "plan_name": plan_info['name'],
            "user_telegram_id": current_user['telegram_id']
        }
        
        result = await execute_one(payment_query, {
            "user_id": current_user['id'],
            "payment_method": request.payment_method,
            "amount_stars": plan_info['price'],
            "metadata": json.dumps(metadata)
        })
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка создания платежа"
            )
        
        payment_id = result[0]
        
        # Создаем Telegram invoice
        telegram_invoice_link = await _create_telegram_invoice(
            payment_id=payment_id,
            plan_info=plan_info,
            user_telegram_id=current_user['telegram_id']
        )
        
        logger.info(f"💳 Создан платеж {payment_id} для пользователя {current_user['telegram_id']}")
        
        return PaymentResponse(
            success=True,
            payment_id=payment_id,
            amount_stars=plan_info['price'],
            telegram_invoice_link=telegram_invoice_link
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка создания платежа: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка создания платежа"
        )


@router.post("/webhook/telegram-payment")
async def telegram_payment_webhook(payment_data: Dict[str, Any]):
    """
    Webhook для обработки платежей Telegram Stars
    """
    try:
        logger.info(f"💫 Получен webhook платежа: {payment_data}")
        
        # Извлекаем данные платежа
        telegram_payment_id = payment_data.get('telegram_payment_charge_id')
        invoice_payload = payment_data.get('invoice_payload')
        
        if not telegram_payment_id or not invoice_payload:
            logger.error("❌ Неполные данные платежа")
            return {"success": False, "error": "Неполные данные"}
        
        # Парсим payload
        try:
            payload_data = json.loads(invoice_payload)
            payment_id = payload_data.get('payment_id')
        except:
            logger.error("❌ Неверный формат payload")
            return {"success": False, "error": "Неверный payload"}
        
        # Обновляем статус платежа
        update_query = """
            UPDATE payments 
            SET status = 'completed',
                telegram_payment_id = :telegram_payment_id,
                completed_at = CURRENT_TIMESTAMP
            WHERE id = :payment_id AND status = 'pending'
        """
        
        rows_updated = await execute_query(update_query, {
            "payment_id": payment_id,
            "telegram_payment_id": telegram_payment_id
        })
        
        if rows_updated == 0:
            logger.error(f"❌ Платеж {payment_id} не найден или уже обработан")
            return {"success": False, "error": "Платеж не найден"}
        
        # Активируем подписку
        await _activate_subscription(payment_id)
        
        logger.info(f"✅ Платеж {payment_id} успешно обработан")
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки webhook платежа: {e}")
        return {"success": False, "error": str(e)}


async def _create_telegram_invoice(
    payment_id: int,
    plan_info: Dict[str, Any],
    user_telegram_id: int
) -> str:
    """Создание Telegram invoice для Telegram Stars"""
    try:
        # В реальной реализации здесь будет вызов Telegram Bot API
        # Для демонстрации возвращаем mock URL
        
        invoice_payload = json.dumps({
            "payment_id": payment_id,
            "plan_code": plan_info.get('name'),
            "user_id": user_telegram_id
        })
        
        # Mock URL для демонстрации
        # В реальности здесь будет вызов:
        # bot.create_invoice_link(...)
        
        mock_invoice_link = f"https://t.me/invoice/{payment_id}_{plan_info['price']}_stars"
        
        logger.info(f"📧 Создан invoice для платежа {payment_id}")
        
        return mock_invoice_link
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания invoice: {e}")
        raise


async def _activate_subscription(payment_id: int):
    """Активация подписки после успешного платежа"""
    try:
        # Получаем данные платежа
        payment_query = """
            SELECT user_id, amount_stars, metadata
            FROM payments
            WHERE id = :payment_id AND status = 'completed'
        """
        
        payment_result = await execute_one(payment_query, {"payment_id": payment_id})
        
        if not payment_result:
            raise Exception(f"Платеж {payment_id} не найден")
        
        user_id, amount_stars, metadata_json = payment_result
        metadata = json.loads(metadata_json)
        plan_code = metadata.get('plan_code')
        
        # Деактивируем старые подписки
        await execute_query(
            "UPDATE subscriptions SET status = 'expired' WHERE user_id = :user_id AND status = 'active'",
            {"user_id": user_id}
        )
        
        # Создаем новую подписку
        starts_at = datetime.now()
        expires_at = starts_at + timedelta(days=30)  # 30 дней
        
        subscription_query = """
            INSERT INTO subscriptions (
                user_id, plan_name, status, price_stars, 
                starts_at, expires_at, auto_renew
            ) VALUES (
                :user_id, :plan_name, 'active', :price_stars,
                :starts_at, :expires_at, 0
            ) RETURNING id
        """
        
        subscription_result = await execute_one(subscription_query, {
            "user_id": user_id,
            "plan_name": plan_code,
            "price_stars": amount_stars,
            "starts_at": starts_at,
            "expires_at": expires_at
        })
        
        # Обновляем план пользователя
        await execute_query(
            """UPDATE users 
               SET subscription_plan = :plan_code,
                   subscription_expires_at = :expires_at,
                   analyses_today = 0
               WHERE id = :user_id""",
            {
                "user_id": user_id,
                "plan_code": plan_code,
                "expires_at": expires_at
            }
        )
        
        # Связываем платеж с подпиской
        if subscription_result:
            subscription_id = subscription_result[0]
            await execute_query(
                "UPDATE payments SET subscription_id = :subscription_id WHERE id = :payment_id",
                {"subscription_id": subscription_id, "payment_id": payment_id}
            )
        
        logger.info(f"✅ Подписка активирована для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка активации подписки: {e}")
        raise


def _get_plan_description(code: str, info: Dict[str, Any]) -> str:
    """Получение описания плана подписки"""
    descriptions = {
        "basic": "Идеально для начинающих трейдеров. 20 анализов в день.",
        "premium": "Для активных трейдеров. 100 анализов в день + приоритетная поддержка.",
        "unlimited": "Для профессионалов. Безлимитные анализы + эксклюзивные функции."
    }
    
    return descriptions.get(code, f"{info['analyses_per_day']} анализов в день")
