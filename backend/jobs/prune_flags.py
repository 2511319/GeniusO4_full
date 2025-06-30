# backend/jobs/prune_flags.py

import os
import sys
from datetime import datetime, timedelta

# Добавляем путь к backend
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.config import logger, db


async def prune_old_flags():
    """Удаление флагов старше 14 дней"""
    try:
        if not db:
            logger.error("Firestore client не инициализирован")
            return
        
        # Вычисляем дату отсечения (14 дней назад)
        cutoff_date = datetime.utcnow() - timedelta(days=14)
        
        # Получаем старые флаги
        flags_ref = db.collection('flags')
        old_flags = flags_ref.where('ts', '<', cutoff_date).stream()
        
        deleted_count = 0
        
        for flag in old_flags:
            flag.reference.delete()
            deleted_count += 1
        
        logger.info(f"Удалено старых флагов: {deleted_count}")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Ошибка при удалении старых флагов: {e}")
        return 0


def main():
    """Точка входа для Cloud Scheduler"""
    import asyncio
    
    try:
        result = asyncio.run(prune_old_flags())
        print(f"Успешно удалено {result} старых флагов")
    except Exception as e:
        logger.error(f"Ошибка выполнения задачи prune_flags: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
