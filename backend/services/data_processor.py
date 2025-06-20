# src/data/data_processor.py

import pandas as pd
import numpy as np
import json
from typing import Dict, Any, List
import math
from backend.config.config import logger
from backend.utils.performance_monitor import monitor_performance, DataSizeAnalyzer
import ta  # Технический анализ


class DataProcessor:
    """
    Класс для предобработки и анализа собранных данных.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self._validate_input_data()

    def _validate_input_data(self) -> None:
        """
        Валидирует входные данные для обеспечения корректности обработки
        """
        try:
            if self.df is None:
                raise ValueError("DataFrame не может быть None")

            if self.df.empty:
                logger.warning("Получен пустой DataFrame")
                return

            # Проверяем наличие обязательных столбцов OHLCV
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in self.df.columns]

            if missing_columns:
                logger.warning(f"Отсутствуют обязательные столбцы: {missing_columns}")

            # Проверяем типы данных
            numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in numeric_columns:
                if col in self.df.columns and not pd.api.types.is_numeric_dtype(self.df[col]):
                    logger.warning(f"Столбец {col} не является числовым: {self.df[col].dtype}")
                    try:
                        self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                        logger.info(f"Столбец {col} преобразован в числовой тип")
                    except Exception as e:
                        logger.error(f"Не удалось преобразовать столбец {col} в числовой: {e}")

            # Проверяем логическую корректность OHLC данных
            if all(col in self.df.columns for col in ['Open', 'High', 'Low', 'Close']):
                # High должен быть >= max(Open, Close)
                invalid_high = (self.df['High'] < self.df[['Open', 'Close']].max(axis=1))
                if invalid_high.any():
                    invalid_count = invalid_high.sum()
                    logger.warning(f"Найдено {invalid_count} свечей с некорректными High значениями")

                # Low должен быть <= min(Open, Close)
                invalid_low = (self.df['Low'] > self.df[['Open', 'Close']].min(axis=1))
                if invalid_low.any():
                    invalid_count = invalid_low.sum()
                    logger.warning(f"Найдено {invalid_count} свечей с некорректными Low значениями")

            # Проверяем размер данных
            data_size = len(self.df)
            if data_size > 10000:
                logger.info(f"Большой объем данных: {data_size} записей. Рекомендуется оптимизация.")
            elif data_size < 10:
                logger.warning(f"Малый объем данных: {data_size} записей. Индикаторы могут быть неточными.")

            logger.info(f"Валидация данных завершена. Записей: {data_size}, Столбцов: {len(self.df.columns)}")

        except Exception as e:
            logger.error(f"Ошибка при валидации входных данных: {e}")

    def preprocess(self) -> pd.DataFrame:
        """
        Выполняет предобработку данных, включая заполнение пропусков.
        """
        try:
            if self.df.isnull().sum().sum() == 0:
                logger.info("Пропущенные значения отсутствуют.")
            else:
                logger.info("Пропущенные значения найдены. Выполняется заполнение...")
                # Используем .ffill() и .bfill() напрямую без fillna с методом
                self.df = self.df.ffill().bfill()
                logger.info("Пропущенные значения заполнены методами ffill и bfill.")
            return self.df
        except Exception as e:
            logger.error(f"Ошибка при предобработке данных: {e}")
            return self.df

    @monitor_performance("DataProcessor.calculate_indicators")
    def calculate_indicators(self) -> pd.DataFrame:
        """
        Рассчитывает технические индикаторы и добавляет их в DataFrame.
        """
        try:
            # RSI
            self.df['RSI'] = ta.momentum.RSIIndicator(close=self.df['Close']).rsi()

            # MACD
            macd = ta.trend.MACD(close=self.df['Close'])
            self.df['MACD'] = macd.macd()
            self.df['MACD_signal'] = macd.macd_signal()
            self.df['MACD_hist'] = macd.macd_diff()

            # OBV
            self.df['OBV'] = ta.volume.OnBalanceVolumeIndicator(
                close=self.df['Close'], volume=self.df['Volume']
            ).on_balance_volume()

            # Скользящие средние
            self.df['MA_20'] = ta.trend.SMAIndicator(close=self.df['Close'], window=20).sma_indicator()
            self.df['MA_50'] = ta.trend.SMAIndicator(close=self.df['Close'], window=50).sma_indicator()
            self.df['MA_100'] = ta.trend.SMAIndicator(close=self.df['Close'], window=100).sma_indicator()
            self.df['MA_200'] = ta.trend.SMAIndicator(close=self.df['Close'], window=200).sma_indicator()

            # ATR
            atr = ta.volatility.AverageTrueRange(
                high=self.df['High'], low=self.df['Low'], close=self.df['Close']
            )
            self.df['ATR'] = atr.average_true_range()

            # Стохастический осциллятор
            stoch = ta.momentum.StochasticOscillator(
                high=self.df['High'], low=self.df['Low'], close=self.df['Close']
            )
            self.df['Stochastic_Oscillator'] = stoch.stoch()

            # Полосы Боллинджера
            bollinger = ta.volatility.BollingerBands(close=self.df['Close'])
            self.df['Bollinger_Middle'] = bollinger.bollinger_mavg()
            self.df['Bollinger_Upper'] = bollinger.bollinger_hband()
            self.df['Bollinger_Lower'] = bollinger.bollinger_lband()

            # ADX
            adx = ta.trend.ADXIndicator(
                high=self.df['High'], low=self.df['Low'], close=self.df['Close']
            )
            self.df['ADX'] = adx.adx()

            # Williams %R
            williams = ta.momentum.WilliamsRIndicator(
                high=self.df['High'], low=self.df['Low'], close=self.df['Close']
            )
            self.df['Williams_%R'] = williams.williams_r()

            # Parabolic SAR
            psar = ta.trend.PSARIndicator(
                high=self.df['High'], low=self.df['Low'], close=self.df['Close']
            )
            self.df['Parabolic_SAR'] = psar.psar()

            # Ichimoku Cloud
            ichimoku = ta.trend.IchimokuIndicator(
                high=self.df['High'], low=self.df['Low']
            )
            self.df['Ichimoku_A'] = ichimoku.ichimoku_a()
            self.df['Ichimoku_B'] = ichimoku.ichimoku_b()
            self.df['Ichimoku_Base_Line'] = ichimoku.ichimoku_base_line()
            self.df['Ichimoku_Conversion_Line'] = ichimoku.ichimoku_conversion_line()

            # **Добавление VWAP**
            vwap = ta.volume.VolumeWeightedAveragePrice(
                high=self.df['High'],
                low=self.df['Low'],
                close=self.df['Close'],
                volume=self.df['Volume'],
                window=14,  # Можно выбрать окно по вашему усмотрению
            )
            self.df['VWAP'] = vwap.volume_weighted_average_price()

            # **Добавление Moving Average Envelopes**
            # Рассчитываем SMA для Moving Average Envelopes
            sma_envelope = ta.trend.SMAIndicator(close=self.df['Close'], window=20).sma_indicator()
            # Устанавливаем процент отклонения (напр., 2%)
            envelope_percentage = 0.02
            self.df['Moving_Average_Envelope_Upper'] = sma_envelope * (1 + envelope_percentage)
            self.df['Moving_Average_Envelope_Lower'] = sma_envelope * (1 - envelope_percentage)

            # Заменяем бесконечные значения, которые могут возникнуть при расчёте индикаторов
            if np.isinf(self.df.select_dtypes(include=[float, int])).values.any():
                logger.info("Обнаружены бесконечные значения, выполняется замена на NaN")
                self.df.replace([np.inf, -np.inf], np.nan, inplace=True)

            logger.info("Индикаторы успешно рассчитаны.")
            return self.df
        except ImportError:
            logger.error("Не удалось импортировать библиотеку 'ta'. Убедитесь, что она установлена.")
            return self.df
        except Exception as e:
            logger.error(f"Ошибка при расчёте индикаторов: {e}")
            return self.df

    def apply_rounding(self):
        """
        Применяет правила округления к различным столбцам.
        """
        try:
            rounding_rules = {
                # Не округляем
                'Open Time': None,
                'Open': None,
                'High': None,
                'Low': None,
                'Close': None,
                'Close Time': None,
                'Number of Trades': None,
                'Ignore': None,
                'MA_20': 5,
                'MA_50': 5,
                'MA_100': 5,
                'MA_200': 5,
                'Parabolic_SAR': 5,
                'Ichimoku_A': 5,
                'Ichimoku_B': 5,
                'Ichimoku_Base_Line': 5,
                'Ichimoku_Conversion_Line': 5,
                "Bollinger_Middle": 5,
                "Bollinger_Upper": 5,
                "Bollinger_Lower": 5,

                # Округляем до целого числа
                'Volume': 'int',
                'Quote Asset Volume': 'int',
                'Taker Buy Base Asset Volume': 'int',
                'Taker Buy Quote Asset Volume': 'int',
                'RSI': 0,
                'MACD': 0,
                'MACD_signal': 0,
                'MACD_hist': 0,
                'OBV': 'int',
                'ATR': 'int',
                'Stochastic_Oscillator': 0,

                # Округляем до 2 знаков после запятой
                'ADX': 2,
                'Williams_%R': 2,

                # Округляем до 5 знаков после запятой
                'VWAP': 5,
                'Moving_Average_Envelope_Upper': 5,
                'Moving_Average_Envelope_Lower': 5
            }

            for column, rule in rounding_rules.items():
                if column in self.df.columns and rule is not None:
                    if rule == 'int':
                        self.df[column] = self.df[column].round(0).astype(int)
                        logger.debug(f"Столбец '{column}' округлен до целого числа.")
                    elif isinstance(rule, int):
                        self.df[column] = self.df[column].round(rule)
                        logger.debug(f"Столбец '{column}' округлен до {rule} знаков после запятой.")
            logger.info("Округление выполнено успешно.")
        except Exception as e:
            logger.error(f"Ошибка при округлении данных: {e}")

    def drop_null_indicators(self) -> pd.DataFrame:
        """
        Удаляет свечи с пропущенными значениями в ключевых индикаторах.
        """
        try:
            indicators = [
                "RSI", "MACD", "MACD_signal", "MACD_hist", "OBV",
                "MA_20", "MA_50", "MA_100", "MA_200", "ATR",
                "Stochastic_Oscillator", "Bollinger_Middle",
                "Bollinger_Upper", "Bollinger_Lower", "ADX",
                "Williams_%R", "Parabolic_SAR",
                "Ichimoku_A", "Ichimoku_B", "Ichimoku_Base_Line", "Ichimoku_Conversion_Line",
                # Новые индикаторы
                "VWAP", "Moving_Average_Envelope_Upper", "Moving_Average_Envelope_Lower"
            ]

            # Оставляем только те индикаторы, которые существуют в датафрейме
            # и не полностью состоят из NaN значений
            valid_cols = [
                col for col in indicators
                if col in self.df.columns and not self.df[col].isna().all()
            ]

            if valid_cols:
                initial_count = len(self.df)
                # Используем .loc для предотвращения SettingWithCopyWarning
                self.df = self.df.dropna(subset=valid_cols).copy()
                final_count = len(self.df)
                removed = initial_count - final_count
                logger.info(
                    f"Удалено {removed} свечей с пропущенными индикаторами "
                    f"по столбцам: {', '.join(valid_cols)}"
                )
            else:
                logger.info(
                    "Нет индикаторов с непустыми значениями для проверки. "
                    "Свечи не удалялись."
                )
            return self.df
        except Exception as e:
            logger.error(f"Ошибка при удалении свечей с null индикаторами: {e}")
            return self.df

    def sanitize(self) -> pd.DataFrame:
        """
        Оптимизированная очистка данных от бесконечных значений и NaN.
        Использует векторизованные операции pandas для лучшей производительности.
        """
        try:
            # Получаем только числовые столбцы для оптимизации
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns

            if len(numeric_cols) == 0:
                logger.info("Нет числовых столбцов для очистки")
                return self.df

            # Проверяем наличие бесконечных значений только в числовых столбцах
            inf_mask = np.isinf(self.df[numeric_cols]).any().any()
            if inf_mask:
                logger.warning("Найдены бесконечные значения, выполняется замена")
                # Заменяем только в числовых столбцах для производительности
                self.df[numeric_cols] = self.df[numeric_cols].replace([np.inf, -np.inf], np.nan)

            # Подсчитываем NaN только в числовых столбцах
            nulls = self.df[numeric_cols].isna().sum().sum()
            if nulls > 0:
                logger.warning(f"Обнаружено {nulls} NaN значений в числовых столбцах, выполняется заполнение")

                # Оптимизированное заполнение: сначала forward fill, затем backward fill
                # Применяем только к числовым столбцам
                self.df[numeric_cols] = self.df[numeric_cols].fillna(method='ffill').fillna(method='bfill')

                # Если все еще остались NaN (например, весь столбец пустой), заполняем нулями
                remaining_nulls = self.df[numeric_cols].isna().sum().sum()
                if remaining_nulls > 0:
                    logger.warning(f"Остались {remaining_nulls} NaN значений, заполняем нулями")
                    self.df[numeric_cols] = self.df[numeric_cols].fillna(0)

            return self.df

        except Exception as e:
            logger.error(f"Ошибка при очистке данных: {e}")
            return self.df

    def save_to_json(self, filename: str):
        """
        Сохраняет обработанные данные в JSON файл.
        """
        try:
            # Преобразуем все столбцы с датами и временем в строки
            for col in ['Open Time', 'Close Time']:
                if col in self.df.columns:
                    self.df[col] = self.df[col].astype(str)
            # Открываем файл с указанием кодировки 'utf-8'
            with open(filename, "w", encoding='utf-8') as f:
                self.df.to_json(f, orient="records", date_format="iso", default_handler=str)
            logger.info(f"Data saved to {filename}.")
        except Exception as e:
            logger.error(f"Failed to save data to {filename}: {e}")

    def get_ohlc_data(self, num_candles: int = 144) -> List[Dict[str, Any]]:
        """
        Оптимизированное получение данных OHLC с включенными индикаторами.
        Использует векторизованные операции для лучшей производительности.

        Параметры:
            num_candles (int): Количество последних свечей для возврата.
        """
        try:
            # Выбираем последние свечи более эффективно
            if num_candles >= len(self.df):
                ohlc_data = self.df.copy()
            else:
                ohlc_data = self.df.iloc[-num_candles:].copy()

            # Оптимизированное преобразование datetime столбцов
            datetime_cols = ohlc_data.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns
            if len(datetime_cols) > 0:
                # Векторизованное преобразование всех datetime столбцов сразу
                for col in datetime_cols:
                    ohlc_data[col] = ohlc_data[col].dt.strftime('%Y-%m-%d %H:%M:%S')

            # Оптимизированная очистка числовых данных
            numeric_cols = ohlc_data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                # Проверяем наличие бесконечных значений только в числовых столбцах
                inf_check = np.isinf(ohlc_data[numeric_cols]).any().any()
                if inf_check:
                    logger.debug("Бесконечные значения в OHLC данных, заменяем на NaN")
                    ohlc_data[numeric_cols] = ohlc_data[numeric_cols].replace([np.inf, -np.inf], np.nan)

                # Заполняем NaN значения
                nan_count = ohlc_data[numeric_cols].isna().sum().sum()
                if nan_count > 0:
                    logger.debug(f"Заполняем {nan_count} NaN значений в OHLC данных")
                    ohlc_data[numeric_cols] = ohlc_data[numeric_cols].fillna(method='ffill').fillna(method='bfill').fillna(0)

            # Финальная очистка для JSON сериализации
            # Заменяем оставшиеся NaN и NaT на None более эффективно
            ohlc_data = ohlc_data.where(pd.notnull(ohlc_data), None)

            # Конвертируем в список словарей
            result = ohlc_data.to_dict(orient='records')

            logger.debug(f"Подготовлено {len(result)} свечей OHLC данных")
            return result

        except Exception as e:
            logger.error(f"Ошибка при получении OHLC данных: {e}")
            # Fallback: возвращаем базовые данные
            try:
                fallback_data = self.df.tail(num_candles).to_dict(orient='records')
                return fallback_data
            except Exception as fallback_error:
                logger.error(f"Критическая ошибка при fallback получении OHLC: {fallback_error}")
                return []

    @monitor_performance("DataProcessor.full_processing")
    def perform_full_processing(self, drop_na: bool = True) -> pd.DataFrame:
        """
        Полный процесс предобработки данных с мониторингом производительности.
        """
        data_size = len(self.df)

        # Выбираем оптимальную стратегию обработки
        strategy = DataSizeAnalyzer.recommend_algorithm(data_size, 'indicators')
        logger.info(f"Обработка {data_size} записей с использованием стратегии: {strategy}")

        self.preprocess()
        self.calculate_indicators()
        self.apply_rounding()  # Применяем округление
        if drop_na:
            self.drop_null_indicators()
        self.sanitize()
        return self.df
