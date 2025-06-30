# backend/validators/analysis_validators.py

import re
from datetime import datetime, timezone
from typing import List, Set, Optional, Union
from pydantic import BaseModel, Field, validator, root_validator
from fastapi import HTTPException

# Константы для валидации
SUPPORTED_INTERVALS = {
    "1m", "5m", "15m", "1h", "4h", "1d"
}

SUPPORTED_INDICATORS = {
    'MACD', 'RSI', 'OBV', 'ATR', 'ADX', 'Stochastic_Oscillator', 'Volume',
    'Bollinger_Bands', 'Ichimoku_Cloud', 'Parabolic_SAR', 'VWAP',
    'Moving_Average_Envelopes', 'support_resistance_levels', 'trend_lines',
    'unfinished_zones', 'imbalances', 'fibonacci_analysis',
    'elliott_wave_analysis', 'structural_edge', 'candlestick_patterns',
    'divergence_analysis', 'fair_value_gaps', 'gap_analysis',
    'psychological_levels', 'anomalous_candles', 'price_prediction',
    'recommendations'
}

# Известные валютные пары и базовые активы
KNOWN_QUOTE_CURRENCIES = {
    "USDT", "USDC", "BUSD", "BTC", "ETH", "BNB", 
    "USD", "EUR", "TRY", "GBP", "JPY", "AUD", "CAD"
}

KNOWN_BASE_CURRENCIES = {
    "BTC", "ETH", "ADA", "DOT", "LINK", "LTC", "XRP", "BCH", "EOS", "TRX",
    "BNB", "AVAX", "SOL", "MATIC", "UNI", "ATOM", "VET", "FIL", "THETA",
    "XLM", "ALGO", "AAVE", "MKR", "COMP", "YFI", "SNX", "CRV", "SUSHI"
}

# Лимиты для безопасности
MIN_LIMIT = 1
MAX_LIMIT = 2000  # Разумный лимит для предотвращения перегрузки API
DEFAULT_LIMIT = 144

# Регулярные выражения для валидации
SYMBOL_PATTERN = re.compile(r'^[A-Z0-9]{2,20}$')
SYMBOL_PAIR_PATTERN = re.compile(r'^[A-Z0-9]{2,10}[-_/]?[A-Z0-9]{2,10}$')


class SymbolValidator:
    """Валидатор для торговых символов"""
    
    @staticmethod
    def validate_symbol_format(symbol: str) -> str:
        """Валидирует формат символа"""
        if not symbol:
            raise ValueError("Символ не может быть пустым")
        
        # Очищаем и приводим к верхнему регистру
        clean_symbol = symbol.strip().upper()
        
        if not clean_symbol:
            raise ValueError("Символ не может состоять только из пробелов")
        
        # Проверяем базовый формат (для одиночных символов тоже разрешаем)
        if not SYMBOL_PAIR_PATTERN.match(clean_symbol) and not SYMBOL_PATTERN.match(clean_symbol):
            raise ValueError(
                f"Неверный формат символа: {symbol}. "
                "Ожидается формат: BTC, BTCUSDT, BTC-USDT, BTC_USDT или BTC/USDT"
            )
        
        return clean_symbol
    
    @staticmethod
    def parse_symbol_pair(symbol: str) -> tuple[str, str]:
        """Парсит символ на базовую и котируемую валюты"""
        # Разделяем по разделителям
        if any(sep in symbol for sep in ["-", "_", "/"]):
            parts = re.split(r"[-_/]", symbol)
            if len(parts) >= 2:
                return parts[0], parts[1]
        
        # Пытаемся автоматически разделить
        for quote in sorted(KNOWN_QUOTE_CURRENCIES, key=len, reverse=True):
            if symbol.endswith(quote) and len(symbol) > len(quote):
                base = symbol[:-len(quote)]
                if len(base) >= 2:  # Минимальная длина базовой валюты
                    return base, quote
        
        # Если не удалось разделить, возвращаем как есть с USD по умолчанию
        return symbol, "USD"
    
    @staticmethod
    def validate_symbol_pair(base: str, quote: str) -> None:
        """Валидирует пару базовая/котируемая валюта"""
        if len(base) < 2 or len(base) > 10:
            raise ValueError(f"Неверная длина базовой валюты: {base}")
        
        if len(quote) < 2 or len(quote) > 10:
            raise ValueError(f"Неверная длина котируемой валюты: {quote}")
        
        if base == quote:
            raise ValueError("Базовая и котируемая валюты не могут быть одинаковыми")
        
        # Предупреждение для неизвестных валют (не критично)
        if base not in KNOWN_BASE_CURRENCIES and quote not in KNOWN_QUOTE_CURRENCIES:
            # Логируем предупреждение, но не блокируем
            pass


class IntervalValidator:
    """Валидатор для временных интервалов"""
    
    @staticmethod
    def validate_interval(interval: str) -> str:
        """Валидирует временной интервал"""
        if not interval:
            raise ValueError("Интервал не может быть пустым")
        
        clean_interval = interval.strip().lower()
        
        if clean_interval not in SUPPORTED_INTERVALS:
            raise ValueError(
                f"Неподдерживаемый интервал: {interval}. "
                f"Поддерживаемые интервалы: {', '.join(sorted(SUPPORTED_INTERVALS))}"
            )
        
        return clean_interval


class LimitValidator:
    """Валидатор для лимита свечей"""
    
    @staticmethod
    def validate_limit(limit: int) -> int:
        """Валидирует лимит количества свечей"""
        if not isinstance(limit, int):
            raise ValueError("Лимит должен быть целым числом")
        
        if limit < MIN_LIMIT:
            raise ValueError(f"Лимит не может быть меньше {MIN_LIMIT}")
        
        if limit > MAX_LIMIT:
            raise ValueError(f"Лимит не может быть больше {MAX_LIMIT}")
        
        return limit


class IndicatorsValidator:
    """Валидатор для списка индикаторов"""
    
    @staticmethod
    def validate_indicators(indicators: List[str]) -> List[str]:
        """Валидирует список индикаторов"""
        if not indicators:
            return []
        
        if not isinstance(indicators, list):
            raise ValueError("Индикаторы должны быть списком строк")
        
        if len(indicators) > len(SUPPORTED_INDICATORS):
            raise ValueError(f"Слишком много индикаторов: {len(indicators)}")
        
        clean_indicators = []
        invalid_indicators = []
        
        for indicator in indicators:
            if not isinstance(indicator, str):
                raise ValueError(f"Индикатор должен быть строкой: {indicator}")
            
            clean_indicator = indicator.strip()
            if not clean_indicator:
                continue  # Пропускаем пустые строки
            
            if clean_indicator not in SUPPORTED_INDICATORS:
                invalid_indicators.append(clean_indicator)
            else:
                clean_indicators.append(clean_indicator)
        
        if invalid_indicators:
            raise ValueError(
                f"Неподдерживаемые индикаторы: {', '.join(invalid_indicators)}. "
                f"Поддерживаемые индикаторы: {', '.join(sorted(SUPPORTED_INDICATORS))}"
            )
        
        # Удаляем дубликаты, сохраняя порядок
        seen = set()
        unique_indicators = []
        for indicator in clean_indicators:
            if indicator not in seen:
                seen.add(indicator)
                unique_indicators.append(indicator)
        
        return unique_indicators


class ValidationError(HTTPException):
    """Кастомное исключение для ошибок валидации"""
    
    def __init__(self, field: str, message: str):
        super().__init__(
            status_code=422,
            detail={
                "error": "Validation Error",
                "field": field,
                "message": message
            }
        )


def validate_analysis_request_data(
    symbol: str,
    interval: str, 
    limit: int,
    indicators: List[str]
) -> tuple[str, str, int, List[str]]:
    """
    Комплексная валидация данных запроса анализа
    
    Returns:
        tuple: (validated_symbol, validated_interval, validated_limit, validated_indicators)
    
    Raises:
        ValidationError: при ошибках валидации
    """
    try:
        # Валидация символа
        validated_symbol = SymbolValidator.validate_symbol_format(symbol)
        base, quote = SymbolValidator.parse_symbol_pair(validated_symbol)
        SymbolValidator.validate_symbol_pair(base, quote)
        
        # Валидация интервала
        validated_interval = IntervalValidator.validate_interval(interval)
        
        # Валидация лимита
        validated_limit = LimitValidator.validate_limit(limit)
        
        # Валидация индикаторов
        validated_indicators = IndicatorsValidator.validate_indicators(indicators)
        
        return validated_symbol, validated_interval, validated_limit, validated_indicators
        
    except ValueError as e:
        # Определяем поле, в котором произошла ошибка
        error_msg = str(e)
        if "символ" in error_msg.lower():
            raise ValidationError("symbol", error_msg)
        elif "интервал" in error_msg.lower():
            raise ValidationError("interval", error_msg)
        elif "лимит" in error_msg.lower():
            raise ValidationError("limit", error_msg)
        elif "индикатор" in error_msg.lower():
            raise ValidationError("indicators", error_msg)
        else:
            raise ValidationError("general", error_msg)


class TimestampValidator:
    """Валидатор для временных меток"""

    # Поддерживаемые форматы дат
    SUPPORTED_FORMATS = [
        "%Y-%m-%d %H:%M:%S",           # 2024-01-01 12:00:00
        "%Y-%m-%dT%H:%M:%S",           # 2024-01-01T12:00:00
        "%Y-%m-%dT%H:%M:%SZ",          # 2024-01-01T12:00:00Z
        "%Y-%m-%dT%H:%M:%S.%f",        # 2024-01-01T12:00:00.123456
        "%Y-%m-%dT%H:%M:%S.%fZ",       # 2024-01-01T12:00:00.123456Z
        "%Y-%m-%d",                    # 2024-01-01
    ]

    @staticmethod
    def validate_timestamp(timestamp: Union[str, int, float, datetime]) -> datetime:
        """
        Валидирует и нормализует временную метку

        Args:
            timestamp: временная метка в различных форматах

        Returns:
            datetime: нормализованная временная метка в UTC

        Raises:
            ValueError: при неверном формате временной метки
        """
        if isinstance(timestamp, datetime):
            # Если уже datetime, проверяем и нормализуем
            return TimestampValidator._normalize_datetime(timestamp)

        if isinstance(timestamp, (int, float)):
            # Unix timestamp
            return TimestampValidator._validate_unix_timestamp(timestamp)

        if isinstance(timestamp, str):
            # Строковое представление даты
            return TimestampValidator._validate_string_timestamp(timestamp)

        raise ValueError(f"Неподдерживаемый тип временной метки: {type(timestamp)}")

    @staticmethod
    def _validate_unix_timestamp(timestamp: Union[int, float]) -> datetime:
        """Валидирует Unix timestamp"""
        # Проверяем разумные границы (между 2000 и 2100 годами)
        min_timestamp = 946684800   # 2000-01-01 00:00:00 UTC
        max_timestamp = 4102444800  # 2100-01-01 00:00:00 UTC

        # Автоматически определяем, в секундах или миллисекундах timestamp
        if timestamp > 1e10:  # Больше 10^10 - вероятно миллисекунды
            timestamp = timestamp / 1000

        if timestamp < min_timestamp or timestamp > max_timestamp:
            raise ValueError(
                f"Временная метка вне допустимого диапазона: {timestamp}. "
                f"Ожидается между {min_timestamp} и {max_timestamp}"
            )

        try:
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except (ValueError, OSError) as e:
            raise ValueError(f"Неверная Unix временная метка: {timestamp} - {e}")

    @staticmethod
    def _validate_string_timestamp(timestamp: str) -> datetime:
        """Валидирует строковую временную метку"""
        if not timestamp or not timestamp.strip():
            raise ValueError("Временная метка не может быть пустой")

        timestamp = timestamp.strip()

        # Пробуем различные форматы
        for fmt in TimestampValidator.SUPPORTED_FORMATS:
            try:
                dt = datetime.strptime(timestamp, fmt)
                return TimestampValidator._normalize_datetime(dt)
            except ValueError:
                continue

        # Если ни один формат не подошел
        raise ValueError(
            f"Неподдерживаемый формат временной метки: {timestamp}. "
            f"Поддерживаемые форматы: {', '.join(TimestampValidator.SUPPORTED_FORMATS)}"
        )

    @staticmethod
    def _normalize_datetime(dt: datetime) -> datetime:
        """Нормализует datetime к UTC"""
        # Проверяем разумные границы
        min_date = datetime(2000, 1, 1, tzinfo=timezone.utc)
        max_date = datetime(2100, 1, 1, tzinfo=timezone.utc)

        # Если нет timezone info, считаем UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            # Конвертируем в UTC
            dt = dt.astimezone(timezone.utc)

        if dt < min_date or dt > max_date:
            raise ValueError(
                f"Дата вне допустимого диапазона: {dt}. "
                f"Ожидается между {min_date} и {max_date}"
            )

        return dt

    @staticmethod
    def validate_timestamp_range(start: Union[str, int, float, datetime],
                                end: Union[str, int, float, datetime]) -> tuple[datetime, datetime]:
        """
        Валидирует диапазон временных меток

        Args:
            start: начальная временная метка
            end: конечная временная метка

        Returns:
            tuple: (start_datetime, end_datetime) в UTC

        Raises:
            ValueError: при неверном диапазоне
        """
        start_dt = TimestampValidator.validate_timestamp(start)
        end_dt = TimestampValidator.validate_timestamp(end)

        if start_dt >= end_dt:
            raise ValueError(
                f"Начальная дата ({start_dt}) должна быть раньше конечной ({end_dt})"
            )

        # Проверяем, что диапазон не слишком большой (максимум 10 лет)
        max_range_days = 365 * 10
        if (end_dt - start_dt).days > max_range_days:
            raise ValueError(
                f"Слишком большой временной диапазон: {(end_dt - start_dt).days} дней. "
                f"Максимум: {max_range_days} дней"
            )

        return start_dt, end_dt
