# src/analysis/statistical_analysis.py

import json
import pandas as pd
from typing import Dict, Any, List
from config.config import logger
from statsmodels.tsa.seasonal import seasonal_decompose
from scipy.stats import shapiro
from scipy.signal import argrelextrema
import math
import numpy as np

def round_dict_values(data, decimals=2):
    """
    Вспомогательная функция для рекурсивного округления всех числовых значений в словаре или списке.
    Параметры:
        data (dict или list): Исходные данные для округления.
        decimals (int, опционально): Количество знаков после запятой. По умолчанию 2.
    Возвращает:
        dict или list: Округленные данные.
    """
    if isinstance(data, dict):
        return {k: round_dict_values(v, decimals) for k, v in data.items()}
    elif isinstance(data, list):
        return [round_dict_values(item, decimals) for item in data]
    elif isinstance(data, (float, int, np.float64, np.int64)):
        return round(data, decimals)
    elif isinstance(data, (pd.Timestamp, pd.Timedelta, np.datetime64)):
        return str(data)  # Преобразуем Timestamp, Timedelta и datetime64 в строку
    else:
        return data

class StatisticalAnalyzer:
    """
    Класс для выполнения статистического анализа данных.
    Логика работы:
    1. Расчет корреляционной матрицы.
    2. Проведение тестов на нормальность распределения.
    3. Расчет автокорреляций.
    4. Разложение временных рядов.
    5. Расчет пивотных точек.
    6. Подготовка данных для JSON анализа.
    Атрибуты:
        df (pd.DataFrame): Исходные данные для анализа.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def perform_full_analysis(self) -> Dict[str, Any]:
        """
        Выполняет полный статистический анализ данных.
        Возвращает:
            dict: Словарь с результатами всех проведенных анализов и подготовленных данных для промпта.
        Логика:
        - Проверка, что DataFrame не пустой.
        - Последовательный вызов методов для расчета различных статистических показателей.
        - Подготовка дополнительных данных для передачи в промпт.
        """
        if self.df.empty:
            logger.warning("DataFrame пустой. Пропуск статистического анализа.")
            return {}

        analysis = {
            "correlations": self.calculate_correlations(),
            "normality_tests": self.perform_normality_tests(),
            "autocorrelations": self.calculate_autocorrelations(),
            "time_series_decomposition": self.decompose_time_series(),
            "pivot_points": self.calculate_pivot_points(),
            "candlestick_patterns": [],  # Если у вас есть логика для обнаружения паттернов, добавьте её
            "ohlc_data": self.get_ohlc_data(),
            "moving_averages": self.get_moving_averages(),
            # Удалены current_indicator_values и historical_indicator_values
        }
        return analysis

    def calculate_correlations(self) -> Dict[str, Any]:
        """
        Рассчитывает корреляционную матрицу для числовых столбцов.
        Возвращает:
            dict: Корреляционная матрица в виде словаря.
        """
        try:
            correlations = self.df.corr().round(2)
            logger.info("Матрица корреляций успешно рассчитана.")
            return correlations.to_dict()
        except Exception as e:
            logger.error(f"Ошибка при расчёте матрицы корреляций: {e}")
            return {}

    def perform_normality_tests(self) -> Dict[str, Any]:
        """
        Выполняет тесты на нормальность распределения для выбранных столбцов.
        Возвращает:
            dict: Результаты тестов Шапиро-Уилка для каждого столбца.
        """
        normality_results = {}
        try:
            for column in ["RSI", "MACD", "OBV"]:
                if column not in self.df.columns:
                    logger.warning(f"Столбец {column} отсутствует в данных для теста на нормальность.")
                    continue
                data = self.df[column].dropna()
                if len(data) < 3:
                    logger.warning(f"Недостаточно данных для выполнения теста нормальности на столбце {column}.")
                    normality_results[column] = "Недостаточно данных для теста."
                    continue
                stat, p = shapiro(data)
                # Округляем значения до 2 знаков после запятой
                stat = round(stat, 2)
                p = round(p, 2)
                normality_results[column] = {
                    "Shapiro-Wilk": {"Statistic": stat, "p-value": p}
                }
                logger.info(f"Тест нормальности для '{column}': Статистика={stat}, p-значение={p}")
            return normality_results
        except Exception as e:
            logger.error(f"Ошибка при выполнении тестов на нормальность: {e}")
            return {}

    def calculate_autocorrelations(self) -> Dict[str, Any]:
        """
        Рассчитывает автокорреляцию для выбранных столбцов с лагом 1.
        Возвращает:
            dict: Значения автокорреляции для каждого столбца.
        """
        autocorr_results = {}
        try:
            for column in ["RSI", "MACD", "OBV"]:
                if column not in self.df.columns:
                    logger.warning(f"Столбец {column} отсутствует в данных для автокорреляции.")
                    continue
                autocorr = self.df[column].autocorr(lag=1)
                # Округляем значение до 2 знаков после запятой
                if math.isnan(autocorr):
                    autocorr = None
                else:
                    autocorr = round(autocorr, 2)
                autocorr_results[column] = autocorr
                logger.info(f"Автокорреляция для '{column}' с лагом 1: {autocorr}")
            return autocorr_results
        except Exception as e:
            logger.error(f"Ошибка при расчёте автокорреляции: {e}")
            return {}

    def decompose_time_series(self) -> Dict[str, Any]:
        """
        Выполняет разложение временных рядов для выбранных столбцов.
        Возвращает:
            dict: Результаты разложения временных рядов.
        """
        decomposition_results = {}
        try:
            for column in ["RSI", "MACD", "OBV"]:
                if column not in self.df.columns:
                    logger.warning(f"Столбец {column} отсутствует в данных для разложения временного ряда.")
                    continue
                data = self.df[column].dropna()
                if len(data) < 30:  # Минимальное количество данных для разложения
                    logger.warning(f"Недостаточно данных для разложения временного ряда на столбце {column}.")
                    decomposition_results[column] = "Недостаточно данных для разложения."
                    continue
                decomposition = seasonal_decompose(data, model="additive", period=30, extrapolate_trend='freq')
                decomposition_results[column] = {
                    "trend": decomposition.trend.dropna().tolist(),
                    "seasonal": decomposition.seasonal.dropna().tolist(),
                    "resid": decomposition.resid.dropna().tolist(),
                }
                logger.info(f"Разложение временного ряда для '{column}' выполнено успешно.")
            # Округляем все числовые значения
            decomposition_results = round_dict_values(decomposition_results)
            return decomposition_results
        except Exception as e:
            logger.error(f"Ошибка при разложении временного ряда: {e}")
            return {}

    def calculate_pivot_points(self) -> Dict[str, Any]:
        """
        Рассчитывает пивотные точки на основе предыдущего периода.
        Возвращает:
            dict: Пивотные точки (Pivot Point, Support Levels, Resistance Levels).
        """
        try:
            if len(self.df) < 2:
                logger.error("Недостаточно данных для расчёта пивотных точек.")
                return {}
            # Рассчитаем пивотные точки на основе предыдущего периода
            high = self.df['High'].iloc[-2]
            low = self.df['Low'].iloc[-2]
            close = self.df['Close'].iloc[-2]

            pivot_point = (high + low + close) / 3
            r1 = (2 * pivot_point) - low
            s1 = (2 * pivot_point) - high
            r2 = pivot_point + (high - low)
            s2 = pivot_point - (high - low)
            r3 = high + 2 * (pivot_point - low)
            s3 = low - 2 * (high - pivot_point)

            pivot_points = {
                "pivot_point": round(pivot_point, 2),
                "support_levels": [round(s1, 2), round(s2, 2), round(s3, 2)],
                "resistance_levels": [round(r1, 2), round(r2, 2), round(r3, 2)]
            }

            logger.info(f"Пивотные точки рассчитаны: {pivot_points}")
            return pivot_points
        except Exception as e:
            logger.error(f"Ошибка при расчёте пивотных точек: {e}")
            return {}

    def get_moving_averages(self) -> Dict[str, Any]:
        """
        Получает значения скользящих средних.
        """
        if self.df.empty:
            return {}
        latest = self.df.iloc[-1]
        moving_averages = {
            "MA_50": latest.get("MA_50"),
            "MA_200": latest.get("MA_200"),
            "MA_20": latest.get("MA_20"),
            "MA_100": latest.get("MA_100")
            # Добавьте другие скользящие средние по необходимости
        }
        return moving_averages

    def get_ohlc_data(self, max_points: int = 400) -> List[Dict[str, Any]]:
        """
        Получает данные OHLC с включенными индикаторами.
        Параметры:
            max_points (int): Максимальное количество точек данных для включения.
        """
        # Выбираем все столбцы, включая индикаторы
        ohlc_data = self.df.tail(max_points).copy()

        # Преобразуем все столбцы с датами и временем в строки
        datetime_cols = ohlc_data.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns
        for col in datetime_cols:
            ohlc_data[col] = ohlc_data[col].astype(str)

        ohlc_data = ohlc_data.to_dict(orient='records')
        return ohlc_data

    def save_statistical_analysis(
        self,
        analysis_results: Dict[str, Any],
        filepath: str = "statistical_analysis.json",
    ) -> None:
        """
        Сохраняет результаты статистического анализа в JSON файл.
        Параметры:
            analysis_results (dict): Результаты статистического анализа.
            filepath (str, опционально): Путь к файлу для сохранения. По умолчанию 'statistical_analysis.json'.
        """
        try:
            analysis_results = round_dict_values(analysis_results)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(analysis_results, f, ensure_ascii=False, indent=4)
            logger.info(f"Статистический анализ сохранён в {filepath}.")
        except Exception as e:
            logger.error(f"Ошибка при сохранении статистического анализа в файл: {e}")

    def find_divergences(self, oscillator: str = "RSI", window: int = 5) -> List[Dict[str, Any]]:
        """Ищет дивергенции между ценой и заданным осциллятором.

        Параметры:
            oscillator: Название столбца с осциллятором ("RSI" или "MACD").
            window: Размер окна для поиска локальных экстремумов.

        Возвращает:
            Список словарей с найденными дивергенциями.
        """
        if oscillator not in self.df.columns:
            logger.warning(f"Осциллятор {oscillator} отсутствует в данных")
            return []

        if len(self.df) < window * 2:
            logger.warning("Недостаточно данных для поиска дивергенций")
            return []

        divergences = []
        try:
            close = self.df["Close"]
            osc = self.df[oscillator]

            lows = argrelextrema(close.values, np.less_equal, order=window)[0]
            highs = argrelextrema(close.values, np.greater_equal, order=window)[0]
            osc_lows = argrelextrema(osc.values, np.less_equal, order=window)[0]
            osc_highs = argrelextrema(osc.values, np.greater_equal, order=window)[0]

            for i in range(1, len(lows)):
                p1, p2 = lows[i - 1], lows[i]
                if p1 in osc_lows and p2 in osc_lows:
                    if close.iloc[p2] < close.iloc[p1] and osc.iloc[p2] > osc.iloc[p1]:
                        divergences.append({
                            "date": str(self.df["Open Time"].iloc[p2]),
                            "type": "bullish_divergence",
                            "indicator": oscillator,
                            "price": float(close.iloc[p2]),
                            "oscillator": float(osc.iloc[p2]),
                        })

            for i in range(1, len(highs)):
                p1, p2 = highs[i - 1], highs[i]
                if p1 in osc_highs and p2 in osc_highs:
                    if close.iloc[p2] > close.iloc[p1] and osc.iloc[p2] < osc.iloc[p1]:
                        divergences.append({
                            "date": str(self.df["Open Time"].iloc[p2]),
                            "type": "bearish_divergence",
                            "indicator": oscillator,
                            "price": float(close.iloc[p2]),
                            "oscillator": float(osc.iloc[p2]),
                        })

        except Exception as e:
            logger.error(f"Ошибка при поиске дивергенций: {e}")

        return divergences
