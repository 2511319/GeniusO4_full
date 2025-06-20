# backend/jobs/expire_subs.py

import os
import sys
from datetime import datetime

# Добавляем путь к backend
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.config import logger, db
from google.cloud import firestore


async def expire_subscriptions():
    """Перевести просроченные vip/premium подписки в user"""
    try:
        if not db:
            logger.error("Firestore client не инициализирован")
            return
        
        now = datetime.utcnow()
        
        # Получаем просроченные подписки
        subs_ref = db.collection('subscriptions')
        expired_subs = subs_ref.where('expires_at', '<', now).stream()
        
        updated_count = 0
        
        for sub in expired_subs:
            sub_data = sub.to_dict()
            telegram_id = sub.id
            
            # Обновляем роль пользователя на 'user'
            user_ref = db.collection('users').document(telegram_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                current_role = user_data.get('role', 'user')
                
                # Понижаем роль только если это premium или vip
                if current_role in ['premium', 'vip']:
                    user_ref.update({
                        'role': 'user',
                        'updated_at': firestore.SERVER_TIMESTAMP
                    })
                    
                    logger.info(f"Роль пользователя {telegram_id} изменена с {current_role} на user (подписка истекла)")
                    updated_count += 1
            
            # Удаляем просроченную подписку
            sub.reference.delete()
        
        logger.info(f"Обработано просроченных подписок: {updated_count}")
        return updated_count
        
    except Exception as e:
        logger.error(f"Ошибка при обработке просроченных подписок: {e}")
        return 0


def main():
    """Точка входа для Cloud Scheduler"""
    import asyncio
    
    try:
        result = asyncio.run(expire_subscriptions())
        print(f"Успешно обработано {result} просроченных подписок")
    except Exception as e:
        logger.error(f"Ошибка выполнения задачи expire_subs: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
