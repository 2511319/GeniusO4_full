# backend/utils/performance_monitor.py

import time
import functools
from typing import Dict, Any, Optional, Callable
from backend.config.config import logger

# Опциональный импорт psutil
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

class PerformanceMonitor:
    """
    Утилита для мониторинга производительности обработки данных
    """
    
    def __init__(self):
        self.metrics = {}
        self.start_time = None
        self.start_memory = None
    
    def start_monitoring(self, operation_name: str) -> None:
        """Начинает мониторинг операции"""
        self.start_time = time.time()
        if PSUTIL_AVAILABLE:
            self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        else:
            self.start_memory = 0  # Fallback если psutil недоступен
        logger.debug(f"Начат мониторинг операции: {operation_name}")
    
    def end_monitoring(self, operation_name: str, data_size: Optional[int] = None) -> Dict[str, Any]:
        """Завершает мониторинг и возвращает метрики"""
        if self.start_time is None:
            logger.warning("Мониторинг не был начат")
            return {}
        
        end_time = time.time()
        if PSUTIL_AVAILABLE:
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        else:
            end_memory = self.start_memory  # Fallback
        
        duration = end_time - self.start_time
        memory_delta = end_memory - self.start_memory
        
        metrics = {
            'operation': operation_name,
            'duration_seconds': round(duration, 4),
            'memory_delta_mb': round(memory_delta, 2),
            'start_memory_mb': round(self.start_memory, 2),
            'end_memory_mb': round(end_memory, 2),
            'timestamp': time.time()
        }
        
        if data_size:
            metrics['data_size'] = data_size
            metrics['throughput_items_per_second'] = round(data_size / duration, 2) if duration > 0 else 0
        
        self.metrics[operation_name] = metrics
        
        # Логируем результаты
        log_msg = f"Операция '{operation_name}' завершена за {duration:.4f}с"
        if data_size:
            log_msg += f", обработано {data_size} элементов ({metrics['throughput_items_per_second']:.2f} эл/с)"
        log_msg += f", память: {memory_delta:+.2f}MB"
        
        if duration > 5.0:  # Предупреждение для медленных операций
            logger.warning(f"МЕДЛЕННАЯ ОПЕРАЦИЯ: {log_msg}")
        elif duration > 1.0:
            logger.info(f"ДОЛГАЯ ОПЕРАЦИЯ: {log_msg}")
        else:
            logger.debug(log_msg)
        
        # Сброс состояния
        self.start_time = None
        self.start_memory = None
        
        return metrics
    
    def get_metrics(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """Возвращает метрики операции или все метрики"""
        if operation_name:
            return self.metrics.get(operation_name, {})
        return self.metrics.copy()
    
    def clear_metrics(self) -> None:
        """Очищает все метрики"""
        self.metrics.clear()


def monitor_performance(operation_name: str = None, log_data_size: bool = True):
    """
    Декоратор для автоматического мониторинга производительности функций
    
    Args:
        operation_name: название операции (если None, используется имя функции)
        log_data_size: логировать ли размер данных (ищет параметры df, data, items)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            # Пытаемся определить размер данных
            data_size = None
            if log_data_size:
                # Ищем pandas DataFrame
                for arg in args:
                    if hasattr(arg, '__len__') and hasattr(arg, 'shape'):  # pandas DataFrame
                        data_size = len(arg)
                        break
                    elif hasattr(arg, '__len__') and not isinstance(arg, str):  # list, tuple
                        data_size = len(arg)
                        break
                
                # Ищем в kwargs
                if data_size is None:
                    for key in ['df', 'data', 'items', 'records']:
                        if key in kwargs and hasattr(kwargs[key], '__len__'):
                            data_size = len(kwargs[key])
                            break
            
            monitor.start_monitoring(op_name)
            try:
                result = func(*args, **kwargs)
                monitor.end_monitoring(op_name, data_size)
                return result
            except Exception as e:
                monitor.end_monitoring(op_name, data_size)
                logger.error(f"Ошибка в операции '{op_name}': {e}")
                raise
        
        return wrapper
    return decorator


class DataSizeAnalyzer:
    """Анализатор размера данных для оптимизации алгоритмов"""
    
    @staticmethod
    def estimate_processing_time(data_size: int, operation_type: str = 'general') -> float:
        """
        Оценивает время обработки на основе размера данных
        
        Args:
            data_size: количество элементов данных
            operation_type: тип операции ('sanitize', 'indicators', 'general')
        
        Returns:
            оценочное время в секундах
        """
        # Базовые коэффициенты производительности (элементов в секунду)
        performance_coefficients = {
            'sanitize': 50000,      # быстрая операция
            'indicators': 10000,    # средняя операция (технические индикаторы)
            'llm_analysis': 1000,   # медленная операция (анализ LLM)
            'general': 20000        # общая оценка
        }
        
        coefficient = performance_coefficients.get(operation_type, 20000)
        estimated_time = data_size / coefficient
        
        return max(0.001, estimated_time)  # минимум 1мс
    
    @staticmethod
    def recommend_algorithm(data_size: int, operation_type: str = 'general') -> str:
        """
        Рекомендует алгоритм обработки на основе размера данных
        
        Args:
            data_size: количество элементов данных
            operation_type: тип операции
        
        Returns:
            рекомендация по алгоритму
        """
        if operation_type == 'sanitize':
            if data_size < 1000:
                return 'recursive'
            elif data_size < 10000:
                return 'iterative'
            else:
                return 'pandas_vectorized'
        
        elif operation_type == 'indicators':
            if data_size < 500:
                return 'simple_calculation'
            elif data_size < 5000:
                return 'optimized_calculation'
            else:
                return 'chunked_processing'
        
        else:  # general
            if data_size < 1000:
                return 'simple'
            elif data_size < 10000:
                return 'optimized'
            else:
                return 'batch_processing'
    
    @staticmethod
    def should_use_caching(data_size: int, operation_frequency: str = 'medium') -> bool:
        """
        Определяет, стоит ли использовать кэширование
        
        Args:
            data_size: размер данных
            operation_frequency: частота операций ('low', 'medium', 'high')
        
        Returns:
            True если кэширование рекомендуется
        """
        frequency_thresholds = {
            'low': 5000,
            'medium': 1000,
            'high': 100
        }
        
        threshold = frequency_thresholds.get(operation_frequency, 1000)
        return data_size > threshold


# Глобальный экземпляр монитора
performance_monitor = PerformanceMonitor()

# Удобные функции для быстрого использования
def start_monitoring(operation_name: str) -> None:
    """Начинает мониторинг операции"""
    performance_monitor.start_monitoring(operation_name)

def end_monitoring(operation_name: str, data_size: Optional[int] = None) -> Dict[str, Any]:
    """Завершает мониторинг операции"""
    return performance_monitor.end_monitoring(operation_name, data_size)

def get_performance_metrics(operation_name: Optional[str] = None) -> Dict[str, Any]:
    """Получает метрики производительности"""
    return performance_monitor.get_metrics(operation_name)

def clear_performance_metrics() -> None:
    """Очищает метрики производительности"""
    performance_monitor.clear_metrics()
