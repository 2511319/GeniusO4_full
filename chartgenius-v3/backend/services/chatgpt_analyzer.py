# backend/services/chatgpt_analyzer.py
"""
AI анализатор для технического анализа криптовалют
Использует OpenAI o4-mini-2025-04-16 для генерации 24 объектов анализа
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

import openai
from openai import AsyncOpenAI

from config.config import get_settings, logger

settings = get_settings()


class ChatGPTAnalyzer:
    """AI анализатор на базе OpenAI"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """Загрузка шаблона промпта"""
        try:
            # Путь к prompt.txt из GeniusO4_full-stable
            prompt_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "GeniusO4_full-stable", "backend", "prompt.txt"
            )
            
            if os.path.exists(prompt_path):
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    prompt = f.read()
                logger.info("✅ Промпт загружен из GeniusO4_full-stable")
                return prompt
            else:
                logger.warning("⚠️ prompt.txt не найден, используется встроенный промпт")
                return self._get_default_prompt()
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки промпта: {e}")
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Встроенный промпт как fallback"""
        return """
Ты профессиональный трейдер и технический аналитик криптовалют. 
Проанализируй предоставленные OHLCV данные и создай детальный технический анализ.

ВАЖНО: Ответ должен быть СТРОГО в JSON формате и содержать ровно 24 объекта анализа:

1. primary_analysis - Основной анализ тренда
2. confidence_in_trading_decisions - Уверенность в торговых решениях
3. support_resistance_levels - Уровни поддержки и сопротивления
4. trend_lines - Трендовые линии
5. pivot_points - Пивот поинты
6. fibonacci_levels - Уровни Фибоначчи
7. volume_analysis - Анализ объемов
8. momentum_indicators - Индикаторы моментума
9. oscillators - Осцилляторы
10. moving_averages - Скользящие средние
11. bollinger_bands - Полосы Боллинджера
12. ichimoku_cloud - Облако Ишимоку
13. candlestick_patterns - Свечные паттерны
14. chart_patterns - Графические паттерны
15. elliott_wave - Волны Эллиотта
16. market_structure - Рыночная структура
17. risk_management - Управление рисками
18. entry_exit_points - Точки входа и выхода
19. price_targets - Ценовые цели
20. stop_loss_levels - Уровни стоп-лосса
21. market_sentiment - Рыночные настроения
22. correlation_analysis - Корреляционный анализ
23. volatility_analysis - Анализ волатильности
24. time_frame_analysis - Анализ временных рамок

Каждый объект должен содержать:
- summary: краткое описание
- details: детальный анализ
- signals: торговые сигналы
- confidence: уровень уверенности (0-100)

OHLCV данные: {ohlcv_data}
Символ: {symbol}
Интервал: {interval}
"""
    
    async def analyze_ohlcv_data(
        self,
        ohlcv_data: List[Dict[str, Any]],
        symbol: str,
        interval: str
    ) -> Optional[Dict[str, Any]]:
        """
        Анализ OHLCV данных с помощью AI
        
        Args:
            ohlcv_data: Список OHLCV данных
            symbol: Торговая пара
            interval: Временной интервал
        
        Returns:
            Словарь с 24 объектами анализа или None при ошибке
        """
        try:
            logger.info(f"🤖 Начат AI анализ {symbol} {interval}")
            
            # Подготовка данных для промпта
            formatted_data = self._format_ohlcv_for_prompt(ohlcv_data)
            
            # Формирование промпта
            prompt = self.prompt_template.format(
                ohlcv_data=formatted_data,
                symbol=symbol,
                interval=interval
            )
            
            # Запрос к OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Ты профессиональный технический аналитик криптовалют. Отвечай ТОЛЬКО в JSON формате."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            # Извлечение и парсинг ответа
            content = response.choices[0].message.content
            
            if not content:
                logger.error("❌ Пустой ответ от OpenAI")
                return None
            
            # Парсинг JSON
            try:
                analysis_result = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Ошибка парсинга JSON от OpenAI: {e}")
                logger.error(f"Ответ: {content[:500]}...")
                return None
            
            # Валидация структуры
            if not self._validate_analysis_structure(analysis_result):
                logger.error("❌ Неверная структура ответа от AI")
                return None
            
            # Добавление метаданных
            analysis_result["_metadata"] = {
                "symbol": symbol,
                "interval": interval,
                "timestamp": datetime.now().isoformat(),
                "ai_model": self.model,
                "data_points": len(ohlcv_data)
            }
            
            logger.info(f"✅ AI анализ {symbol} завершен успешно")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Ошибка AI анализа {symbol}: {e}", exc_info=True)
            return None
    
    def _format_ohlcv_for_prompt(self, ohlcv_data: List[Dict[str, Any]]) -> str:
        """Форматирование OHLCV данных для промпта"""
        if not ohlcv_data:
            return "Нет данных"
        
        # Берем последние 50 свечей для анализа (чтобы не превысить лимит токенов)
        recent_data = ohlcv_data[-50:]
        
        formatted_lines = []
        for candle in recent_data:
            line = (
                f"Time: {candle.get('datetime', 'N/A')}, "
                f"O: {candle.get('open', 0):.4f}, "
                f"H: {candle.get('high', 0):.4f}, "
                f"L: {candle.get('low', 0):.4f}, "
                f"C: {candle.get('close', 0):.4f}, "
                f"V: {candle.get('volume', 0):.2f}"
            )
            formatted_lines.append(line)
        
        # Добавляем статистику
        prices = [float(candle.get('close', 0)) for candle in recent_data if candle.get('close')]
        if prices:
            current_price = prices[-1]
            min_price = min(prices)
            max_price = max(prices)
            
            stats = f"""
Статистика за период:
- Текущая цена: {current_price:.4f}
- Минимум: {min_price:.4f}
- Максимум: {max_price:.4f}
- Изменение: {((current_price - prices[0]) / prices[0] * 100):.2f}%
- Количество свечей: {len(recent_data)}

OHLCV данные:
"""
            return stats + "\n".join(formatted_lines)
        
        return "\n".join(formatted_lines)
    
    def _validate_analysis_structure(self, analysis: Dict[str, Any]) -> bool:
        """Валидация структуры AI анализа"""
        required_keys = [
            "primary_analysis", "confidence_in_trading_decisions", "support_resistance_levels",
            "trend_lines", "pivot_points", "fibonacci_levels", "volume_analysis",
            "momentum_indicators", "oscillators", "moving_averages", "bollinger_bands",
            "ichimoku_cloud", "candlestick_patterns", "chart_patterns", "elliott_wave",
            "market_structure", "risk_management", "entry_exit_points", "price_targets",
            "stop_loss_levels", "market_sentiment", "correlation_analysis", 
            "volatility_analysis", "time_frame_analysis"
        ]
        
        missing_keys = [key for key in required_keys if key not in analysis]
        
        if missing_keys:
            logger.warning(f"⚠️ Отсутствуют ключи в AI анализе: {missing_keys}")
            # Пытаемся дополнить недостающие ключи
            for key in missing_keys:
                analysis[key] = {
                    "summary": "Анализ недоступен",
                    "details": "Данные не были сгенерированы AI моделью",
                    "signals": [],
                    "confidence": 0
                }
            logger.info("✅ Недостающие ключи дополнены")
        
        return True
    
    async def test_connection(self) -> bool:
        """Тестирование подключения к OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10
            )
            
            return bool(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования OpenAI: {e}")
            return False


# Глобальный экземпляр анализатора
chatgpt_analyzer = ChatGPTAnalyzer()
