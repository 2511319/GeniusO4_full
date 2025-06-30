# backend/jobs/daily_digest.py

import os
import sys
import asyncio
from datetime import datetime
from typing import List, Dict, Any

# Добавляем путь к backend
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.config import logger, db
from services.crypto_compare_provider import fetch_ohlcv
from google.cloud import firestore
import httpx


async def get_price_data(symbol: str) -> Dict[str, Any]:
    """Получение данных о цене и изменении для символа"""
    try:
        # Получаем данные за последние 2 дня для расчета изменения
        df = await fetch_ohlcv(symbol, '1d', 2)
        
        if df.empty or len(df) < 2:
            return None
        
        current_price = df.iloc[-1]['Close']
        prev_price = df.iloc[-2]['Close']
        change_pct = ((current_price - prev_price) / prev_price) * 100
        
        # Простая проверка пересечения MA (20 и 50 периодов)
        if len(df) >= 50:
            ma20 = df['Close'].rolling(20).mean().iloc[-1]
            ma50 = df['Close'].rolling(50).mean().iloc[-1]
            ma_signal = "🟢 Бычий" if ma20 > ma50 else "🔴 Медвежий"
        else:
            ma_signal = "⚪ Недостаточно данных"
        
        return {
            'symbol': symbol,
            'price': current_price,
            'change_pct': change_pct,
            'ma_signal': ma_signal
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения данных для {symbol}: {e}")
        return None


async def generate_digest_for_user(telegram_id: str, symbols: List[str]) -> str:
    """Генерация дайджеста для пользователя"""
    try:
        digest_lines = [
            f"📊 **Ежедневный дайджест ChartGenius**",
            f"📅 {datetime.now().strftime('%d.%m.%Y')}",
            "",
            "💰 **Ваш watchlist:**"
        ]
        
        for symbol in symbols[:10]:  # Ограничиваем до 10 символов
            price_data = await get_price_data(symbol)
            
            if price_data:
                change_emoji = "🟢" if price_data['change_pct'] > 0 else "🔴"
                change_sign = "+" if price_data['change_pct'] > 0 else ""
                
                digest_lines.append(
                    f"{symbol}: ${price_data['price']:.4f} "
                    f"({change_emoji}{change_sign}{price_data['change_pct']:.2f}%)"
                )
                digest_lines.append(f"   MA: {price_data['ma_signal']}")
            else:
                digest_lines.append(f"{symbol}: ❌ Данные недоступны")
        
        digest_lines.extend([
            "",
            "🚀 Откройте приложение для детального анализа!",
            "",
            "⚙️ Настройки дайджеста: /settings"
        ])
        
        return "\n".join(digest_lines)
        
    except Exception as e:
        logger.error(f"Ошибка генерации дайджеста для {telegram_id}: {e}")
        return None


async def send_digest_to_user(telegram_id: str, digest_text: str):
    """Отправка дайджеста пользователю через Telegram Bot API"""
    try:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN не установлен")
            return False
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={
                'chat_id': telegram_id,
                'text': digest_text,
                'parse_mode': 'Markdown'
            })
            
            if response.status_code == 200:
                logger.info(f"Дайджест отправлен пользователю {telegram_id}")
                return True
            else:
                logger.error(f"Ошибка отправки дайджеста пользователю {telegram_id}: {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"Ошибка отправки дайджеста пользователю {telegram_id}: {e}")
        return False


async def daily_digest():
    """Отправка ежедневного дайджеста для vip/premium пользователей"""
    try:
        if not db:
            logger.error("Firestore client не инициализирован")
            return
        
        # Получаем пользователей с активными подписками
        now = datetime.utcnow()
        subs_ref = db.collection('subscriptions')
        active_subs = subs_ref.where('expires_at', '>', now).stream()
        
        sent_count = 0
        
        for sub in active_subs:
            sub_data = sub.to_dict()
            telegram_id = sub.id
            level = sub_data.get('level', '')
            
            # Отправляем дайджест только vip и premium
            if level not in ['vip', 'premium']:
                continue
            
            # Получаем watchlist пользователя
            watchlist_ref = db.collection('watchlists').document(telegram_id)
            watchlist_doc = watchlist_ref.get()
            
            if not watchlist_doc.exists:
                continue
            
            watchlist_data = watchlist_doc.to_dict()
            symbols = watchlist_data.get('symbols', [])
            
            if not symbols:
                continue
            
            # Генерируем дайджест
            digest_text = await generate_digest_for_user(telegram_id, symbols)
            
            if digest_text:
                # Отправляем дайджест
                success = await send_digest_to_user(telegram_id, digest_text)
                if success:
                    sent_count += 1
                
                # Небольшая задержка между отправками
                await asyncio.sleep(0.1)
        
        logger.info(f"Отправлено дайджестов: {sent_count}")
        return sent_count
        
    except Exception as e:
        logger.error(f"Ошибка при отправке ежедневных дайджестов: {e}")
        return 0


def main():
    """Точка входа для Cloud Scheduler"""
    try:
        result = asyncio.run(daily_digest())
        print(f"Успешно отправлено {result} дайджестов")
    except Exception as e:
        logger.error(f"Ошибка выполнения задачи daily_digest: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
