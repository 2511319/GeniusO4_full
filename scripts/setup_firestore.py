#!/usr/bin/env python3
"""
Скрипт для настройки Firestore коллекций и индексов
Проект: chartgenius-444017
"""

import os
import sys
from datetime import datetime, timedelta
from google.cloud import firestore
from google.cloud.firestore import FieldFilter
import google.auth

def setup_firestore():
    """Настройка Firestore коллекций и индексов"""
    
    print("🗄️ Настройка Firestore для ChartGenius...")
    
    try:
        # Инициализация клиента Firestore
        credentials, project = google.auth.default()
        db = firestore.Client(credentials=credentials, project=project)
        print(f"✅ Подключение к Firestore проекта {project}")
        
        # Создаем коллекции с примерами документов
        setup_users_collection(db)
        setup_subscriptions_collection(db)
        setup_analyses_collection(db)
        
        print("\n🎉 Настройка Firestore завершена!")
        print("\n📝 Следующие шаги:")
        print("1. Настройте TTL policy для коллекции 'analyses' в Firebase Console")
        print("2. Создайте композитные индексы при необходимости")
        print("3. Настройте правила безопасности Firestore")
        
    except Exception as e:
        print(f"❌ Ошибка настройки Firestore: {e}")
        sys.exit(1)

def setup_users_collection(db):
    """Настройка коллекции пользователей"""
    print("\n👤 Настройка коллекции 'users'...")
    
    # Создаем пример документа пользователя
    sample_user = {
        'id': 123456789,
        'username': 'sample_user',
        'first_name': 'Sample',
        'last_name': 'User',
        'photo_url': '',
        'created_at': datetime.utcnow(),
        'last_login': datetime.utcnow(),
        'is_active': True
    }
    
    # Добавляем пример (если не существует)
    user_ref = db.collection('users').document('sample_user')
    if not user_ref.get().exists:
        user_ref.set(sample_user)
        print("✅ Создан пример документа в коллекции 'users'")
    else:
        print("ℹ️ Коллекция 'users' уже содержит данные")

def setup_subscriptions_collection(db):
    """Настройка коллекции подписок"""
    print("\n💳 Настройка коллекции 'subscriptions'...")
    
    # Создаем пример документа подписки
    sample_subscription = {
        'telegram_id': '123456789',
        'subscription_level': 'premium',
        'created_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(days=30),
        'is_active': True,
        'features': ['full_analysis', 'all_indicators', 'price_prediction', 'detailed_recommendations'],
        'analysis_count': 0,
        'analysis_limit': -1,  # -1 = безлимитно
        'payment_info': {
            'last_payment': datetime.utcnow(),
            'payment_method': 'card',
            'amount': 29.99,
            'currency': 'USD'
        }
    }
    
    # Добавляем пример (если не существует)
    sub_ref = db.collection('subscriptions').document('123456789')
    if not sub_ref.get().exists:
        sub_ref.set(sample_subscription)
        print("✅ Создан пример документа в коллекции 'subscriptions'")
    else:
        print("ℹ️ Коллекция 'subscriptions' уже содержит данные")

def setup_analyses_collection(db):
    """Настройка коллекции анализов"""
    print("\n📊 Настройка коллекции 'analyses'...")
    
    # Создаем пример документа анализа
    sample_analysis = {
        'id': 'analysis_123456789_1640995200',
        'telegram_id': '123456789',
        'symbol': 'BTCUSDT',
        'analysis_type': 'full',
        'created_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(days=30),  # TTL
        'analysis_result': {
            'summary': 'Восходящий тренд с сильной поддержкой',
            'trend_analysis': {
                'direction': 'Восходящий',
                'strength': 'Сильный'
            },
            'recommendations': {
                'action': 'Long',
                'entry_price': 45000,
                'stop_loss': 43000,
                'take_profit': 48000
            }
        },
        'primary_analysis': {
            'trend': 'Восходящий',
            'signal': 'Long',
            'risk_level': 'Средний',
            'main_recommendation': 'Рекомендуется открытие длинной позиции'
        },
        'metadata': {
            'interval': '4h',
            'limit': 100,
            'indicators_used': ['RSI', 'MACD', 'Bollinger_Bands'],
            'processing_time': 2.5
        }
    }
    
    # Добавляем пример (если не существует)
    analysis_ref = db.collection('analyses').document('sample_analysis')
    if not analysis_ref.get().exists:
        analysis_ref.set(sample_analysis)
        print("✅ Создан пример документа в коллекции 'analyses'")
    else:
        print("ℹ️ Коллекция 'analyses' уже содержит данные")
    
    print("\n⚠️ ВАЖНО: Настройте TTL policy для поля 'expires_at' в Firebase Console")
    print("   1. Откройте Firebase Console")
    print("   2. Перейдите в Firestore Database")
    print("   3. Выберите коллекцию 'analyses'")
    print("   4. Настройте TTL для поля 'expires_at'")

def create_indexes(db):
    """Создание необходимых индексов"""
    print("\n🔍 Информация об индексах...")
    print("Следующие композитные индексы могут потребоваться:")
    print("1. subscriptions: telegram_id, expires_at")
    print("2. analyses: telegram_id, created_at (desc)")
    print("3. analyses: telegram_id, expires_at")
    print("\nИндексы создаются автоматически при первых запросах или через Firebase Console")

def cleanup_sample_data(db):
    """Очистка примеров данных (опционально)"""
    print("\n🧹 Очистка примеров данных...")
    
    try:
        # Удаляем примеры документов
        db.collection('users').document('sample_user').delete()
        db.collection('subscriptions').document('123456789').delete()
        db.collection('analyses').document('sample_analysis').delete()
        print("✅ Примеры данных удалены")
    except Exception as e:
        print(f"⚠️ Ошибка при удалении примеров: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        # Режим очистки
        credentials, project = google.auth.default()
        db = firestore.Client(credentials=credentials, project=project)
        cleanup_sample_data(db)
    else:
        # Обычная настройка
        setup_firestore()
