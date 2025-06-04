# src/analysis/subscription_manager.py

from config.config import db, logger
from datetime import datetime, timedelta

def create_subscription(username, level='premium', duration_days=30):
    if db is None:
        logger.error("Firestore Client не инициализирован.")
        return
    subscription_ref = db.collection('subscriptions').document(username)
    subscription_ref.set({
        'subscription_level': level,
        'expires_at': datetime.utcnow() + timedelta(days=duration_days)
    })
    logger.info(f"Подписка для {username} создана: {level} на {duration_days} дней.")

def check_subscription(username):
    if db is None:
        logger.error("Firestore Client не инициализирован.")
        return 'none'
    subscription_ref = db.collection('subscriptions').document(username)
    subscription_doc = subscription_ref.get()
    if subscription_doc.exists:
        data = subscription_doc.to_dict()
        if data['expires_at'] > datetime.utcnow():
            return data['subscription_level']
        else:
            return 'expired'
    else:
        return 'none'

def renew_subscription(username, level='premium', duration_days=30):
    if db is None:
        logger.error("Firestore Client не инициализирован.")
        return
    subscription_ref = db.collection('subscriptions').document(username)
    subscription_ref.update({
        'subscription_level': level,
        'expires_at': datetime.utcnow() + timedelta(days=duration_days)
    })
    logger.info(f"Подписка для {username} обновлена: {level} на {duration_days} дней.")
