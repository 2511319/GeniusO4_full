# src/analysis/chatgpt_analyzer.py

import json
from typing import Dict, Any
from config.config import OPENAI_API_KEY, logger
from openai import OpenAI
import re
import os
import time
import math

class ChatGPTAnalyzer:
    """
    Класс для взаимодействия с ChatGPT для анализа данных.
    """

    def __init__(self):
        """
        Инициализирует ChatGPTAnalyzer с API ключом и моделью.
        """
        self.api_key = OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def construct_prompt(self, analysis_results: Dict[str, Any]) -> str:
        """
        Формирует текст промпта на основе переданных данных.
        """
        try:
            template_path = os.path.join(
                os.path.dirname(__file__),
                os.pardir, "prompt.txt"
            )
            with open(template_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()
            ohlc_data = analysis_results.get("ohlc", [])

            def _sanitize(val):
                if isinstance(val, float):
                    if math.isnan(val) or math.isinf(val):
                        return None
                    return float(val)
                if isinstance(val, dict):
                    return {k: _sanitize(v) for k, v in val.items()}
                if isinstance(val, list):
                    return [_sanitize(v) for v in val]
                return val

            safe_data = _sanitize(ohlc_data)
            if safe_data != ohlc_data:
                logger.debug("Данные содержали NaN/inf, выполнена очистка")

            # Подстановка данных в шаблон промпта
            prompt = prompt_template.replace(
                "{{ ohlc_data | tojson | default([]) }}",
                json.dumps(safe_data, ensure_ascii=False, allow_nan=False)
            )

            # Сохраняем сформированный промпт в режиме отладки
            if os.getenv("DEBUG_LOGGING", "false").lower() == "true":
                os.makedirs("dev_logs", exist_ok=True)
                ts = int(time.time())
                prompt_file = f"dev_logs/prompt_{ts}.txt"
                with open(prompt_file, "w", encoding="utf-8") as pf:
                    pf.write(prompt)
                logger.info(f"Промпт сохранён в {prompt_file}.")

            return prompt
        except Exception as e:
            logger.error(f"Не удалось сконструировать промпт: {e}")
            return ""

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

    def analyze(self, analysis_results: Dict[str, Any]) -> tuple[Dict[str, Any], bool]:
        """
        Выполняет анализ данных с помощью ChatGPT.
        Возвращает кортеж (данные_анализа, флаг_ошибки).
        Если полученный JSON некорректен, флаг_ошибки = True.
        """
        try:
            prompt = self.construct_prompt(analysis_results)
            if not prompt:
                logger.warning("Промпт пустой, анализ не выполнен.")
                return {}, True

            # Отправка запроса в модель
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an...erienced trader and a top-tier expert in predictive analysis."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Логируем полный ответ модели в режиме отладки
            if os.getenv("DEBUG_LOGGING", "false").lower() == "true":
                os.makedirs("dev_logs", exist_ok=True)
                ts = int(time.time())
                raw_file = f"dev_logs/chatgpt_raw_response_{ts}.json"
                try:
                    resp_dict = response.model_dump()
                except Exception:
                    resp_dict = json.loads(str(response))
                with open(raw_file, "w", encoding="utf-8") as rf:
                    json.dump(resp_dict, rf, ensure_ascii=False, indent=4)
                logger.info(f"Сырый ответ ChatGPT сохранён в {raw_file}.")

            answer = response.choices[0].message.content.strip()

            # Извлечение JSON из ответа
            json_str = self.extract_json(answer)
            if json_str:
                try:
                    analysis_data = json.loads(json_str)

                    # Сохраняем распарсенный JSON в режиме отладки
                    if os.getenv("DEBUG_LOGGING", "false").lower() == "true":
                        parsed_file = f"dev_logs/chatgpt_response_{ts}.json"
                        with open(parsed_file, "w", encoding="utf-8") as prf:
                            json.dump(analysis_data, prf, ensure_ascii=False, indent=4)
                        logger.info(f"Распарсенный ответ ChatGPT сохранён в {parsed_file}.")
                    else:
                        self.save_response(analysis_data)

                    logger.info("Анализ данных выполнен успешно.")
                    return analysis_data, False
                except json.JSONDecodeError:
                    logger.error("Извлечённый JSON некорректен.")
                    with open("invalid_chatgpt_response.txt", "w", encoding="utf-8") as iv:
                        iv.write(answer)
                    logger.info("Невалидный ответ ChatGPT сохранён в invalid_chatgpt_response.txt.")
                    return {}, True
            else:
                logger.error("Ответ ChatGPT не содержит валидного JSON.")
                with open("invalid_chatgpt_response.txt", "w", encoding="utf-8") as iv:
                    iv.write(answer)
                logger.info("Невалидный ответ ChatGPT сохранён в invalid_chatgpt_response.txt.")
                return {}, True

        except Exception as e:
            logger.error(f"Ошибка при анализе данных с помощью ChatGPT: {e}")
            return {}, True

    def save_response(
        self,
        response: Dict[str, Any],
        filepath: str = "chatgpt_response.json"
    ) -> None:
        """
        Сохраняет ответ ChatGPT в JSON файл.
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(response, f, ensure_ascii=False, indent=4)
            logger.info(f"Ответ ChatGPT сохранён в {filepath}.")
        except Exception as e:
            logger.error(f"Ошибка при сохранении ответа ChatGPT в файл: {e}")
