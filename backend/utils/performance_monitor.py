# backend/utils/performance_monitor.py

import time
import functools
from typing import Any, Callable
from backend.config.config import logger


def monitor_performance(operation_name: str):
    """
    Декоратор для мониторинга производительности операций.
    
    Args:
        operation_name (str): Название операции для логирования
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                logger.info(f"{operation_name} выполнено за {execution_time:.2f} секунд")
                return result
            except Exception as e:
                end_time = time.time()
                execution_time = end_time - start_time
                logger.error(f"{operation_name} завершилось с ошибкой за {execution_time:.2f} секунд: {e}")
                raise
        return wrapper
    return decorator


class DataSizeAnalyzer:
    """
    Анализатор размера данных для рекомендации оптимальных алгоритмов.
    """
    
    @staticmethod
    def recommend_algorithm(data_size: int, operation_type: str = 'general') -> str:
        """
        Рекомендует алгоритм обработки на основе размера данных.
        
        Args:
            data_size (int): Размер данных
            operation_type (str): Тип операции
            
        Returns:
            str: Рекомендуемая стратегия
        """
        if data_size < 100:
            return "simple"
        elif data_size < 1000:
            return "optimized"
        elif data_size < 10000:
            return "vectorized"
        else:
            return "chunked"
