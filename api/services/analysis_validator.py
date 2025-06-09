from typing import Dict, Any
from config.config import logger


def validate_analysis(analysis: Dict[str, Any]) -> None:
    """Проверяет наличие ключевых полей в разделах анализа.

    Для каждого отсутствующего поля выводится предупреждение через logger.
    """
    if not isinstance(analysis, dict):
        logger.warning("validate_analysis: входные данные должны быть словарем")
        return

    sections = {
        'primary_analysis': ['global_trend', 'local_trend', 'patterns', 'anomalies'],
        'feedback': ['issues', 'missed_data', 'model_configuration', 'note', 'time_period'],
        'confidence_in_trading_decisions': ['confidence', 'reason'],
        'indicator_correlations': ['macd_rsi_correlation', 'atr_volatility_correlation', 'explanation'],
        'volatility_by_intervals': ['morning_volatility', 'evening_volatility', 'comparison'],
        'market_cycles_identification': [],
        'extended_ichimoku_analysis': ['conversion_base_line_cross', 'price_vs_cloud'],
        'support_resistance_levels': ['supports', 'resistances'],
        'trend_lines': ['lines'],
        'unfinished_zones': ['type', 'level', 'date'],
        'imbalances': ['type', 'start_point', 'end_point', 'price_range'],
        'fibonacci_analysis': ['based_on_local_trend', 'based_on_global_trend'],
        'elliott_wave_analysis': ['current_wave', 'wave_count', 'forecast'],
        'structural_edge': ['type', 'date', 'price'],
        'candlestick_patterns': ['type'],
        'divergence_analysis': ['indicator', 'type', 'date'],
        'fair_value_gaps': ['date', 'price_range'],
        'gap_analysis': ['gaps', 'comment'],
        'psychological_levels': ['levels'],
        'anomalous_candles': ['date', 'type', 'price'],
        'price_prediction': ['forecast', 'virtual_candles'],
        'recommendations': ['trading_strategies'],
        'volume_analysis': ['volume_trends', 'significant_volume_changes'],
    }

    for key, fields in sections.items():
        value = analysis.get(key)
        if not value:
            continue

        if isinstance(value, list):
            for i, item in enumerate(value):
                if not isinstance(item, dict):
                    logger.warning(f"Раздел {key}: запись {i} имеет некорректный формат")
                    continue
                for field in fields:
                    if field not in item:
                        logger.warning(f"Раздел {key}: запись {i} отсутствует поле {field}")
        elif isinstance(value, dict):
            for field in fields:
                if field not in value:
                    logger.warning(f"Раздел {key}: отсутствует поле {field}")
            if key == 'gap_analysis' and isinstance(value.get('gaps'), list):
                for i, gap in enumerate(value['gaps']):
                    if not isinstance(gap, dict):
                        logger.warning(f"gap_analysis: запись {i} имеет некорректный формат")
                        continue
                    if 'start_point' not in gap or 'end_point' not in gap:
                        logger.warning(f"gap_analysis: запись {i} не содержит start_point/end_point")
        else:
            logger.warning(f"Раздел {key} имеет неожиданный тип {type(value).__name__}")
