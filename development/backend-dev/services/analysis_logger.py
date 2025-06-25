# backend/services/analysis_logger.py

import json
import os
import time
from typing import Dict, Any, Optional
from backend.config.config import logger

class AnalysisLogger:
    """
    Класс для логирования результатов анализа.
    Отделен от бизнес-логики анализа для соблюдения принципа единственной ответственности.
    """
    
    def __init__(self, debug_logging: bool = None):
        """
        Инициализирует логгер анализа
        
        Args:
            debug_logging: включить отладочное логирование (если None, берется из переменной окружения)
        """
        if debug_logging is None:
            debug_logging = os.getenv("DEBUG_LOGGING", "false").lower() == "true"
        
        self.debug_logging = debug_logging
        self.logs_dir = "dev_logs"
        
        if self.debug_logging:
            os.makedirs(self.logs_dir, exist_ok=True)
    
    def log_prompt(self, prompt: str) -> Optional[str]:
        """
        Сохраняет промпт в файл при отладочном режиме
        
        Args:
            prompt: текст промпта
            
        Returns:
            путь к файлу или None
        """
        if not self.debug_logging or not prompt:
            return None
        
        try:
            ts = int(time.time())
            prompt_file = os.path.join(self.logs_dir, f"prompt_{ts}.txt")
            
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(prompt)
            
            logger.info(f"Промпт сохранён в {prompt_file}")
            return prompt_file
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении промпта: {e}")
            return None
    
    def log_raw_response(self, response: Any, timestamp: Optional[int] = None) -> Optional[str]:
        """
        Сохраняет сырой ответ модели в файл при отладочном режиме
        
        Args:
            response: ответ модели
            timestamp: временная метка (если None, генерируется автоматически)
            
        Returns:
            путь к файлу или None
        """
        if not self.debug_logging:
            return None
        
        try:
            if timestamp is None:
                timestamp = int(time.time())
            
            raw_file = os.path.join(self.logs_dir, f"llm_raw_response_{timestamp}.json")
            
            # Пытаемся сериализовать ответ
            try:
                if hasattr(response, 'model_dump'):
                    resp_dict = response.model_dump()
                elif hasattr(response, 'to_dict'):
                    resp_dict = response.to_dict()
                else:
                    resp_dict = json.loads(str(response))
            except Exception:
                resp_dict = {"raw_response": str(response), "type": str(type(response))}
            
            with open(raw_file, "w", encoding="utf-8") as f:
                json.dump(resp_dict, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Сырой ответ модели сохранён в {raw_file}")
            return raw_file
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении сырого ответа: {e}")
            return None
    
    def log_parsed_response(self, analysis_data: Dict[str, Any], timestamp: Optional[int] = None) -> Optional[str]:
        """
        Сохраняет распарсенный ответ в файл
        
        Args:
            analysis_data: распарсенные данные анализа
            timestamp: временная метка (если None, генерируется автоматически)
            
        Returns:
            путь к файлу или None
        """
        if not analysis_data:
            return None
        
        try:
            if timestamp is None:
                timestamp = int(time.time())
            
            if self.debug_logging:
                parsed_file = os.path.join(self.logs_dir, f"llm_response_{timestamp}.json")
            else:
                parsed_file = "llm_response.json"
            
            with open(parsed_file, "w", encoding="utf-8") as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Распарсенный ответ сохранён в {parsed_file}")
            return parsed_file
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении распарсенного ответа: {e}")
            return None
    
    def log_invalid_response(self, response_text: str, error_msg: str = "") -> Optional[str]:
        """
        Сохраняет невалидный ответ для отладки
        
        Args:
            response_text: текст невалидного ответа
            error_msg: сообщение об ошибке
            
        Returns:
            путь к файлу или None
        """
        try:
            timestamp = int(time.time())
            invalid_file = f"invalid_llm_response_{timestamp}.txt"
            
            with open(invalid_file, "w", encoding="utf-8") as f:
                if error_msg:
                    f.write(f"Ошибка: {error_msg}\n\n")
                f.write("Ответ модели:\n")
                f.write(response_text)
            
            logger.info(f"Невалидный ответ сохранён в {invalid_file}")
            return invalid_file
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении невалидного ответа: {e}")
            return None
    
    def log_analysis_success(self, provider: str, model: str, tokens_used: int = 0):
        """
        Логирует успешное выполнение анализа
        
        Args:
            provider: название провайдера
            model: название модели
            tokens_used: количество использованных токенов
        """
        logger.info(
            f"Анализ выполнен успешно. Провайдер: {provider}, "
            f"Модель: {model}, Токенов использовано: {tokens_used}"
        )
    
    def log_analysis_error(self, error: Exception, context: str = ""):
        """
        Логирует ошибку анализа
        
        Args:
            error: исключение
            context: контекст ошибки
        """
        error_msg = f"Ошибка при анализе данных"
        if context:
            error_msg += f" ({context})"
        error_msg += f": {error}"
        
        logger.error(error_msg)
