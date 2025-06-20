# backend/services/chatgpt_analyzer.py

import json
import re
import math
from typing import Dict, Any, Optional
from backend.config.config import logger
from .llm_service import LLMService
from .analysis_logger import AnalysisLogger
from .providers.base import LLMProviderError

class ChatGPTAnalyzer:
    """
    Класс для анализа данных с использованием LLM.
    Рефакторинг: разделена бизнес-логика анализа и логирование.
    """

    def __init__(self, llm_service: Optional[LLMService] = None, analysis_logger: Optional[AnalysisLogger] = None):
        """
        Инициализирует анализатор

        Args:
            llm_service: сервис для работы с LLM (если None, создается автоматически)
            analysis_logger: логгер для анализа (если None, создается автоматически)
        """
        self.llm_service = llm_service or LLMService()
        self.logger = analysis_logger or AnalysisLogger()

        logger.info(f"Инициализирован ChatGPTAnalyzer с провайдером: {self.llm_service.provider_name}")

    def construct_prompt(self, analysis_results: Dict[str, Any]) -> str:
        """
        Формирует текст промпта на основе переданных данных.
        """
        try:
            template_path = self._get_prompt_template_path()
            with open(template_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()

            ohlc_data = analysis_results.get("ohlc", [])
            safe_data = self._sanitize_data(ohlc_data)

            if safe_data != ohlc_data:
                logger.debug("Данные содержали NaN/inf, выполнена очистка")

            # Подстановка данных в шаблон промпта
            prompt = prompt_template.replace(
                "{{ ohlc_data | tojson | default([]) }}",
                json.dumps(safe_data, ensure_ascii=False, allow_nan=False)
            )

            # Логируем промпт
            self.logger.log_prompt(prompt)
            return prompt

        except FileNotFoundError as e:
            logger.error(f"Файл шаблона промпта не найден: {e}")
            return ""
        except json.JSONEncodeError as e:
            logger.error(f"Ошибка сериализации данных в JSON: {e}")
            return ""
        except Exception as e:
            logger.error(f"Не удалось сконструировать промпт: {e}")
            return ""

    def _get_prompt_template_path(self) -> str:
        """Возвращает путь к файлу шаблона промпта"""
        import os
        return os.path.join(
            os.path.dirname(__file__),
            os.pardir, "prompt.txt"
        )

    def _sanitize_data(self, data):
        """
        Очищает данные от NaN/inf значений.
        Высокопроизводительная версия с использованием pandas для больших объемов данных.
        """
        import pandas as pd
        import numpy as np
        from collections import deque

        # Для небольших данных используем быструю рекурсию
        if self._estimate_data_size(data) < 10000:
            return self._sanitize_small_data(data)

        # Для больших данных используем pandas оптимизацию
        return self._sanitize_large_data(data)

    def _estimate_data_size(self, data) -> int:
        """Оценивает размер данных для выбора алгоритма очистки"""
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            return sum(len(v) if isinstance(v, (list, dict)) else 1 for v in data.values())
        else:
            return 1

    def _sanitize_small_data(self, data):
        """Быстрая очистка для небольших объемов данных"""
        def _sanitize_value(val, depth=0):
            # Ограничиваем глубину рекурсии
            if depth > 50:  # Уменьшили лимит для безопасности
                logger.warning(f"Достигнута максимальная глубина рекурсии при очистке данных: {depth}")
                return None

            if isinstance(val, float):
                if math.isnan(val) or math.isinf(val):
                    return None
                return val  # Убрали лишнее float() преобразование
            elif isinstance(val, dict):
                # Используем dict comprehension для лучшей производительности
                return {k: _sanitize_value(v, depth + 1) for k, v in val.items() if v is not None}
            elif isinstance(val, list):
                # Фильтруем None значения сразу
                return [_sanitize_value(v, depth + 1) for v in val if v is not None]
            else:
                return val

        return _sanitize_value(data)

    def _sanitize_large_data(self, data):
        """Оптимизированная очистка для больших объемов данных с использованием pandas"""
        import pandas as pd
        import numpy as np

        try:
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                # Конвертируем в DataFrame для векторизованной обработки
                df = pd.DataFrame(data)

                # Заменяем NaN и inf значения на None
                df = df.replace([np.nan, np.inf, -np.inf], None)

                # Конвертируем обратно в список словарей
                return df.to_dict('records')

            elif isinstance(data, dict):
                # Для словарей обрабатываем каждое значение
                result = {}
                for key, value in data.items():
                    if isinstance(value, (list, dict)):
                        result[key] = self._sanitize_large_data(value)
                    elif isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                        result[key] = None
                    else:
                        result[key] = value
                return result

            else:
                # Fallback на быструю очистку
                return self._sanitize_small_data(data)

        except Exception as e:
            logger.warning(f"Ошибка при оптимизированной очистке данных: {e}. Используем fallback.")
            return self._sanitize_small_data(data)

    def extract_json(self, text: str) -> str:
        """
        Извлекает JSON-часть из текста ответа ChatGPT.
        """
        pattern = r"```json(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end != -1:
            return text[start:end]
        return ""

    def analyze(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполняет анализ данных с помощью LLM.
        Рефакторинг: добавлена дифференцированная обработка ошибок.
        """
        try:
            prompt = self.construct_prompt(analysis_results)
            if not prompt:
                logger.warning("Промпт пустой, анализ не выполнен.")
                return {}

            # Подготавливаем сообщения для LLM
            messages = [
                {
                    "role": "system",
                    "content": "You are an experienced trader and a top-tier expert in predictive analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            # Отправка запроса через LLMService
            response = self.llm_service.generate(messages)

            # Логируем сырой ответ
            timestamp = self.logger.log_raw_response(response)

            # Извлекаем контент из ответа
            answer = response.content.strip() if response.content else ""

            if not answer:
                logger.warning("Получен пустой ответ от модели")
                return {}

            # Извлечение и парсинг JSON из ответа
            return self._parse_llm_response(answer, timestamp)

        except LLMProviderError as e:
            self.logger.log_analysis_error(e, "Ошибка LLM провайдера")
            return {}
        except json.JSONDecodeError as e:
            self.logger.log_analysis_error(e, "Ошибка парсинга JSON")
            return {}
        except FileNotFoundError as e:
            self.logger.log_analysis_error(e, "Файл не найден")
            return {}
        except Exception as e:
            self.logger.log_analysis_error(e, "Неожиданная ошибка")
            return {}

    def _parse_llm_response(self, response_text: str, timestamp: Optional[int] = None) -> Dict[str, Any]:
        """
        Парсит ответ LLM и извлекает JSON данные

        Args:
            response_text: текст ответа от модели
            timestamp: временная метка для логирования

        Returns:
            словарь с данными анализа или пустой словарь при ошибке
        """
        json_str = self.extract_json(response_text)

        if not json_str:
            self.logger.log_invalid_response(
                response_text,
                "Ответ не содержит валидного JSON"
            )
            return {}

        try:
            analysis_data = json.loads(json_str)

            # Логируем успешно распарсенный ответ
            self.logger.log_parsed_response(analysis_data, timestamp)

            # Логируем успех с информацией о модели
            provider_name = getattr(self.llm_service, 'provider_name', 'unknown')
            model_name = getattr(analysis_data, 'model', 'unknown')
            tokens_used = 0

            if hasattr(self.llm_service, 'client') and hasattr(self.llm_service.client, 'usage'):
                tokens_used = self.llm_service.client.usage.get('total_tokens', 0)

            self.logger.log_analysis_success(provider_name, model_name, tokens_used)

            return analysis_data

        except json.JSONDecodeError as e:
            self.logger.log_invalid_response(
                response_text,
                f"Извлечённый JSON некорректен: {e}"
            )
            return {}

    def save_response(
        self,
        response: Dict[str, Any],
        filepath: str = "llm_response.json"
    ) -> None:
        """
        Сохраняет ответ LLM в JSON файл.
        DEPRECATED: используйте AnalysisLogger.log_parsed_response()
        """
        logger.warning("Метод save_response устарел, используйте AnalysisLogger")
        self.logger.log_parsed_response(response)
