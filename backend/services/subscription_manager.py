# src/analysis/subscription_manager.py

import os
import logging
from datetime import datetime, timedelta

# Простая версия для локального тестирования
# В продакшене будет использоваться Firestore

logger = logging.getLogger(__name__)

# Для локального тестирования - все пользователи имеют активную подписку
LOCAL_TESTING = os.getenv("LOCAL_TESTING", "true").lower() == "true"

# Уровни подписок и их возможности
SUBSCRIPTION_LEVELS = {
    'none': {
        'name': 'Без подписки',
        'features': [],
        'analysis_limit': 0
    },
    'basic': {
        'name': 'Базовая',
        'features': ['simple_analysis', 'basic_indicators'],
        'analysis_limit': 10
    },
    'premium': {
        'name': 'Премиум',
        'features': ['full_analysis', 'all_indicators', 'price_prediction', 'detailed_recommendations'],
        'analysis_limit': -1  # Безлимитно
    }
}

def create_subscription(username, level='premium', duration_days=30):
    """Создает подписку для пользователя"""
    if LOCAL_TESTING:
        logger.info(f"[LOCAL] Подписка для {username} создана: {level} на {duration_days} дней.")
        return True

    # Код для Firestore в продакшене
    try:
        from backend.config.config import db
        if db is None:
            logger.error("Firestore Client не инициализирован.")
            return False

        subscription_ref = db.collection('subscriptions').document(str(username))
        subscription_data = {
            'telegram_id': str(username),
            'subscription_level': level,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(days=duration_days),
            'is_active': True,
            'features': SUBSCRIPTION_LEVELS.get(level, {}).get('features', []),
            'analysis_count': 0,
            'analysis_limit': SUBSCRIPTION_LEVELS.get(level, {}).get('analysis_limit', 0)
        }

        subscription_ref.set(subscription_data)
        logger.info(f"Подписка для {username} создана: {level} на {duration_days} дней.")
        return True

    except Exception as e:
        logger.error(f"Ошибка создания подписки: {e}")
        return False

def check_subscription(username):
    """Проверяет статус подписки пользователя"""
    if LOCAL_TESTING:
        logger.info(f"[LOCAL] Проверка подписки для {username} - возвращаем 'premium'")
        return 'premium'  # Для локального тестирования все имеют подписку

    # Код для Firestore в продакшене
    try:
        from backend.config.config import db
        if db is None:
            logger.error("Firestore Client не инициализирован.")
            return 'none'

        subscription_ref = db.collection('subscriptions').document(str(username))
        subscription_doc = subscription_ref.get()

        if subscription_doc.exists:
            data = subscription_doc.to_dict()
            expires_at = data.get('expires_at')

            # Проверяем, не истекла ли подписка
            if expires_at and expires_at > datetime.utcnow():
                return data.get('subscription_level', 'none')
            else:
                # Обновляем статус на истекший
                subscription_ref.update({'is_active': False})
                return 'expired'
        else:
            return 'none'

    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return 'none'

def get_subscription_details(username):
    """Получает детальную информацию о подписке пользователя"""
    if LOCAL_TESTING:
        return {
            'level': 'premium',
            'expires_at': datetime.utcnow() + timedelta(days=30),
            'is_active': True,
            'features': SUBSCRIPTION_LEVELS['premium']['features'],
            'analysis_count': 5,
            'analysis_limit': -1
        }

    try:
        from backend.config.config import db
        if db is None:
            logger.error("Firestore Client не инициализирован.")
            return None

        subscription_ref = db.collection('subscriptions').document(str(username))
        subscription_doc = subscription_ref.get()

        if subscription_doc.exists:
            data = subscription_doc.to_dict()
            expires_at = data.get('expires_at')

            # Проверяем активность подписки
            is_active = expires_at and expires_at > datetime.utcnow()

            return {
                'level': data.get('subscription_level', 'none'),
                'expires_at': expires_at,
                'is_active': is_active,
                'features': data.get('features', []),
                'analysis_count': data.get('analysis_count', 0),
                'analysis_limit': data.get('analysis_limit', 0),
                'created_at': data.get('created_at')
            }
        else:
            return {
                'level': 'none',
                'expires_at': None,
                'is_active': False,
                'features': [],
                'analysis_count': 0,
                'analysis_limit': 0
            }

    except Exception as e:
        logger.error(f"Ошибка получения деталей подписки: {e}")
        return None

def renew_subscription(username, level='premium', duration_days=30):
    """Обновляет подписку пользователя"""
    if LOCAL_TESTING:
        logger.info(f"[LOCAL] Подписка для {username} обновлена: {level} на {duration_days} дней.")
        return True

    try:
        from backend.config.config import db
        if db is None:
            logger.error("Firestore Client не инициализирован.")
            return False

        subscription_ref = db.collection('subscriptions').document(str(username))

        # Получаем текущие данные подписки
        current_doc = subscription_ref.get()
        current_expires = None

        if current_doc.exists:
            current_data = current_doc.to_dict()
            current_expires = current_data.get('expires_at')

        # Определяем новую дату истечения
        if current_expires and current_expires > datetime.utcnow():
            # Если подписка еще активна, продлеваем от текущей даты истечения
            new_expires = current_expires + timedelta(days=duration_days)
        else:
            # Если подписка истекла или отсутствует, продлеваем от текущего момента
            new_expires = datetime.utcnow() + timedelta(days=duration_days)

        update_data = {
            'subscription_level': level,
            'expires_at': new_expires,
            'is_active': True,
            'features': SUBSCRIPTION_LEVELS.get(level, {}).get('features', []),
            'analysis_limit': SUBSCRIPTION_LEVELS.get(level, {}).get('analysis_limit', 0),
            'renewed_at': datetime.utcnow()
        }

        subscription_ref.update(update_data)
        logger.info(f"Подписка для {username} обновлена: {level} на {duration_days} дней.")
        return True

    except Exception as e:
        logger.error(f"Ошибка обновления подписки: {e}")
        return False

def increment_analysis_count(username):
    """Увеличивает счетчик использованных анализов"""
    if LOCAL_TESTING:
        logger.info(f"[LOCAL] Счетчик анализов для {username} увеличен")
        return True

    try:
        from backend.config.config import db
        if db is None:
            logger.error("Firestore Client не инициализирован.")
            return False

        subscription_ref = db.collection('subscriptions').document(str(username))

        # Используем транзакцию для атомарного обновления
        from google.cloud.firestore import firestore

        @firestore.transactional
        def update_count(transaction, ref):
            doc = ref.get(transaction=transaction)
            if doc.exists:
                current_count = doc.to_dict().get('analysis_count', 0)
                transaction.update(ref, {'analysis_count': current_count + 1})
                return current_count + 1
            return 0

        transaction = db.transaction()
        new_count = update_count(transaction, subscription_ref)

        logger.info(f"Счетчик анализов для {username} увеличен до {new_count}")
        return True

    except Exception as e:
        logger.error(f"Ошибка увеличения счетчика анализов: {e}")
        return False

def can_perform_analysis(username, analysis_type='simple'):
    """Проверяет, может ли пользователь выполнить анализ"""
    subscription_details = get_subscription_details(username)

    if not subscription_details:
        return False, "Не удалось получить информацию о подписке"

    if not subscription_details['is_active']:
        return False, "Подписка неактивна или истекла"

    # Проверяем лимит анализов
    analysis_limit = subscription_details['analysis_limit']
    if analysis_limit > 0:  # -1 означает безлимитно
        current_count = subscription_details['analysis_count']
        if current_count >= analysis_limit:
            return False, f"Достигнут лимит анализов ({analysis_limit})"

    # Проверяем доступность типа анализа
    features = subscription_details['features']
    required_feature = 'full_analysis' if analysis_type == 'full' else 'simple_analysis'

    if required_feature not in features:
        return False, f"Тип анализа '{analysis_type}' недоступен для вашей подписки"

    return True, "OK"
