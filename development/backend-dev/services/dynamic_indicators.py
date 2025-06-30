# 🧮 Dynamic Indicators Engine for ChartGenius
# Версия: 1.1.0-dev
# Безопасное создание пользовательских индикаторов

import ast
import operator
import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Union
import logging
import hashlib
import json
from datetime import datetime
import redis.asyncio as redis
from backend.services.metrics_service import metrics

logger = logging.getLogger(__name__)

# === БЕЗОПАСНЫЕ ОПЕРАЦИИ ===
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

SAFE_FUNCTIONS = {
    'abs': abs,
    'min': min,
    'max': max,
    'round': round,
    'sum': sum,
    'len': len,
    'sqrt': math.sqrt,
    'log': math.log,
    'exp': math.exp,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'mean': np.mean,
    'std': np.std,
    'median': np.median,
    'sma': lambda data, period: pd.Series(data).rolling(window=period).mean().tolist(),
    'ema': lambda data, period: pd.Series(data).ewm(span=period).mean().tolist(),
    'rsi': lambda data, period=14: _calculate_rsi(data, period),
    'macd': lambda data: _calculate_macd(data),
    'bollinger': lambda data, period=20: _calculate_bollinger_bands(data, period),
}

class FormulaSecurityError(Exception):
    """Ошибка безопасности формулы"""
    pass

class FormulaValidationError(Exception):
    """Ошибка валидации формулы"""
    pass

class DynamicIndicatorEngine:
    """Движок для создания и выполнения пользовательских индикаторов"""
    
    def __init__(self):
        self.redis_client = None
        self.max_execution_time = 5.0  # 5 секунд максимум
        self.max_data_points = 10000   # Максимум точек данных
        self.cache_ttl = 3600          # 1 час кэширования
    
    async def get_redis(self):
        """Получение Redis клиента"""
        if not self.redis_client:
            self.redis_client = redis.Redis(
                host='localhost', 
                port=6379, 
                decode_responses=True
            )
        return self.redis_client
    
    def validate_formula(self, formula: str) -> Dict[str, Any]:
        """
        Валидация формулы на безопасность и корректность
        
        Args:
            formula: Строка с формулой (например, "sma(close, 20)")
            
        Returns:
            Dict с результатами валидации
            
        Raises:
            FormulaSecurityError: При обнаружении небезопасных операций
            FormulaValidationError: При синтаксических ошибках
        """
        try:
            # Парсинг AST
            tree = ast.parse(formula, mode='eval')
            
            # Проверка безопасности
            self._check_security(tree)
            
            # Проверка синтаксиса
            self._check_syntax(tree)
            
            # Извлечение зависимостей
            dependencies = self._extract_dependencies(tree)
            
            return {
                'valid': True,
                'dependencies': dependencies,
                'complexity_score': self._calculate_complexity(tree),
                'estimated_execution_time': self._estimate_execution_time(tree)
            }
            
        except SyntaxError as e:
            raise FormulaValidationError(f"Синтаксическая ошибка: {e}")
        except FormulaSecurityError:
            raise
        except Exception as e:
            raise FormulaValidationError(f"Ошибка валидации: {e}")
    
    def _check_security(self, node):
        """Проверка безопасности AST узла"""
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            raise FormulaSecurityError("Импорт модулей запрещен")
        
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name not in SAFE_FUNCTIONS:
                    raise FormulaSecurityError(f"Функция '{func_name}' не разрешена")
            elif isinstance(node.func, ast.Attribute):
                raise FormulaSecurityError("Вызов методов объектов запрещен")
        
        if isinstance(node, ast.Attribute):
            # Разрешаем только доступ к данным (close, open, high, low, volume)
            allowed_attributes = ['close', 'open', 'high', 'low', 'volume']
            if hasattr(node, 'attr') and node.attr not in allowed_attributes:
                raise FormulaSecurityError(f"Доступ к атрибуту '{node.attr}' запрещен")
        
        if isinstance(node, ast.BinOp) and type(node.op) not in SAFE_OPERATORS:
            raise FormulaSecurityError(f"Оператор {type(node.op).__name__} не разрешен")
        
        # Рекурсивная проверка дочерних узлов
        for child in ast.iter_child_nodes(node):
            self._check_security(child)
    
    def _check_syntax(self, tree):
        """Проверка синтаксической корректности"""
        try:
            compile(tree, '<formula>', 'eval')
        except SyntaxError as e:
            raise FormulaValidationError(f"Синтаксическая ошибка: {e}")
    
    def _extract_dependencies(self, tree) -> List[str]:
        """Извлечение зависимостей из формулы"""
        dependencies = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                dependencies.add(node.id)
            elif isinstance(node, ast.Attribute):
                if hasattr(node, 'attr'):
                    dependencies.add(node.attr)
        
        # Фильтруем только валидные зависимости
        valid_deps = {'close', 'open', 'high', 'low', 'volume'}
        return list(dependencies.intersection(valid_deps))
    
    def _calculate_complexity(self, tree) -> int:
        """Вычисление сложности формулы"""
        complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                complexity += 2
            elif isinstance(node, ast.BinOp):
                complexity += 1
        return complexity
    
    def _estimate_execution_time(self, tree) -> float:
        """Оценка времени выполнения формулы"""
        base_time = 0.001  # 1ms базовое время
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = getattr(node.func, 'id', '')
                if func_name in ['sma', 'ema', 'rsi', 'macd']:
                    base_time += 0.01  # 10ms для технических индикаторов
                else:
                    base_time += 0.001  # 1ms для простых функций
        
        return base_time
    
    async def execute_formula(self, formula: str, data: Dict[str, List[float]], 
                            cache_key: Optional[str] = None) -> List[float]:
        """
        Выполнение формулы с данными
        
        Args:
            formula: Строка формулы
            data: Словарь с данными (close, open, high, low, volume)
            cache_key: Ключ для кэширования результата
            
        Returns:
            Список вычисленных значений
        """
        try:
            # Проверяем кэш
            if cache_key:
                cached_result = await self._get_cached_result(cache_key)
                if cached_result:
                    metrics.track_cache_hit('dynamic_indicator')
                    return cached_result
                metrics.track_cache_miss('dynamic_indicator')
            
            # Валидация формулы
            validation = self.validate_formula(formula)
            
            # Проверка размера данных
            max_length = max(len(values) for values in data.values())
            if max_length > self.max_data_points:
                raise FormulaValidationError(
                    f"Слишком много точек данных: {max_length} > {self.max_data_points}"
                )
            
            # Подготовка контекста выполнения
            context = self._prepare_execution_context(data)
            
            # Выполнение формулы
            start_time = datetime.utcnow()
            tree = ast.parse(formula, mode='eval')
            result = self._evaluate_ast(tree, context)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Проверка времени выполнения
            if execution_time > self.max_execution_time:
                raise FormulaValidationError(
                    f"Превышено время выполнения: {execution_time:.2f}s > {self.max_execution_time}s"
                )
            
            # Нормализация результата
            normalized_result = self._normalize_result(result, max_length)
            
            # Кэширование результата
            if cache_key:
                await self._cache_result(cache_key, normalized_result)
            
            # Метрики
            metrics.track_user_action('dynamic_indicator_executed', 'user')
            
            logger.info(f"Formula executed successfully in {execution_time:.3f}s")
            return normalized_result
            
        except Exception as e:
            logger.error(f"Error executing formula: {e}")
            metrics.track_error(type(e).__name__, 'dynamic_indicator')
            raise
    
    def _prepare_execution_context(self, data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Подготовка контекста для выполнения формулы"""
        context = {
            # Данные
            **data,
            # Безопасные функции
            **SAFE_FUNCTIONS,
            # Математические константы
            'pi': math.pi,
            'e': math.e,
        }
        return context
    
    def _evaluate_ast(self, node, context):
        """Безопасное выполнение AST узла"""
        if isinstance(node, ast.Expression):
            return self._evaluate_ast(node.body, context)
        
        elif isinstance(node, ast.Num):  # Python < 3.8
            return node.n
        elif isinstance(node, ast.Constant):  # Python >= 3.8
            return node.value
        
        elif isinstance(node, ast.Name):
            if node.id in context:
                return context[node.id]
            else:
                raise NameError(f"Переменная '{node.id}' не определена")
        
        elif isinstance(node, ast.BinOp):
            left = self._evaluate_ast(node.left, context)
            right = self._evaluate_ast(node.right, context)
            op = SAFE_OPERATORS.get(type(node.op))
            if op:
                return op(left, right)
            else:
                raise FormulaSecurityError(f"Оператор {type(node.op).__name__} не разрешен")
        
        elif isinstance(node, ast.UnaryOp):
            operand = self._evaluate_ast(node.operand, context)
            op = SAFE_OPERATORS.get(type(node.op))
            if op:
                return op(operand)
            else:
                raise FormulaSecurityError(f"Унарный оператор {type(node.op).__name__} не разрешен")
        
        elif isinstance(node, ast.Call):
            func_name = node.func.id if isinstance(node.func, ast.Name) else None
            if func_name and func_name in SAFE_FUNCTIONS:
                args = [self._evaluate_ast(arg, context) for arg in node.args]
                kwargs = {kw.arg: self._evaluate_ast(kw.value, context) for kw in node.keywords}
                return SAFE_FUNCTIONS[func_name](*args, **kwargs)
            else:
                raise FormulaSecurityError(f"Функция '{func_name}' не разрешена")
        
        else:
            raise FormulaSecurityError(f"AST узел {type(node).__name__} не поддерживается")
    
    def _normalize_result(self, result: Any, target_length: int) -> List[float]:
        """Нормализация результата к списку float"""
        if isinstance(result, (int, float)):
            return [float(result)] * target_length
        elif isinstance(result, (list, tuple, np.ndarray)):
            result_list = list(result)
            # Дополняем NaN если результат короче
            while len(result_list) < target_length:
                result_list.insert(0, float('nan'))
            return [float(x) if not pd.isna(x) else float('nan') for x in result_list[:target_length]]
        else:
            raise FormulaValidationError(f"Неподдерживаемый тип результата: {type(result)}")
    
    async def _get_cached_result(self, cache_key: str) -> Optional[List[float]]:
        """Получение результата из кэша"""
        try:
            redis_client = await self.get_redis()
            cached_data = await redis_client.get(f"indicator_cache:{cache_key}")
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error getting cached result: {e}")
        return None
    
    async def _cache_result(self, cache_key: str, result: List[float]):
        """Сохранение результата в кэш"""
        try:
            redis_client = await self.get_redis()
            await redis_client.setex(
                f"indicator_cache:{cache_key}",
                self.cache_ttl,
                json.dumps(result)
            )
        except Exception as e:
            logger.error(f"Error caching result: {e}")
    
    def generate_cache_key(self, formula: str, data_hash: str) -> str:
        """Генерация ключа кэша"""
        combined = f"{formula}:{data_hash}"
        return hashlib.md5(combined.encode()).hexdigest()

# === ТЕХНИЧЕСКИЕ ИНДИКАТОРЫ ===
def _calculate_rsi(data: List[float], period: int = 14) -> List[float]:
    """Расчет RSI"""
    if len(data) < period + 1:
        return [float('nan')] * len(data)
    
    df = pd.DataFrame({'close': data})
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(float('nan')).tolist()

def _calculate_macd(data: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, List[float]]:
    """Расчет MACD"""
    df = pd.DataFrame({'close': data})
    ema_fast = df['close'].ewm(span=fast).mean()
    ema_slow = df['close'].ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    
    return {
        'macd': macd_line.fillna(float('nan')).tolist(),
        'signal': signal_line.fillna(float('nan')).tolist(),
        'histogram': histogram.fillna(float('nan')).tolist()
    }

def _calculate_bollinger_bands(data: List[float], period: int = 20, std_dev: float = 2) -> Dict[str, List[float]]:
    """Расчет полос Боллинджера"""
    df = pd.DataFrame({'close': data})
    sma = df['close'].rolling(window=period).mean()
    std = df['close'].rolling(window=period).std()
    
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    
    return {
        'upper': upper_band.fillna(float('nan')).tolist(),
        'middle': sma.fillna(float('nan')).tolist(),
        'lower': lower_band.fillna(float('nan')).tolist()
    }

# Глобальный экземпляр движка
dynamic_indicator_engine = DynamicIndicatorEngine()
