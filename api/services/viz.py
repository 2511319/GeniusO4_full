# src/visualization/visualizer.py

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Any
from config.config import logger
from .analysis_validator import validate_analysis

def create_chart(selected_elements: List[str], df: pd.DataFrame, analysis_data: Dict[str, Any]) -> go.Figure:
    try:
        indicators_with_subplots = []
        if 'MACD' in selected_elements:
            indicators_with_subplots.append('MACD')
        if 'RSI' in selected_elements:
            indicators_with_subplots.append('RSI')
        if 'OBV' in selected_elements:
            indicators_with_subplots.append('OBV')
        if 'ATR' in selected_elements:
            indicators_with_subplots.append('ATR')
        if 'ADX' in selected_elements:
            indicators_with_subplots.append('ADX')
        if 'Stochastic_Oscillator' in selected_elements:
            indicators_with_subplots.append('Stochastic_Oscillator')
        if 'Volume' in selected_elements or 'volume' in selected_elements:
            indicators_with_subplots.append('Volume')

        num_rows = 1 + len(indicators_with_subplots)
        row_heights = [0.8] + [0.2 / (num_rows - 1)] * (num_rows - 1) if num_rows > 1 else [1]

        fig = make_subplots(rows=num_rows, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=row_heights)

        fig.add_trace(go.Candlestick(
            x=df['Open Time'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ), row=1, col=1)

        if 'Bollinger_Bands' in selected_elements:
            fig.add_trace(go.Scatter(
                x=df['Open Time'],
                y=df['Bollinger_Upper'],
                line=dict(color='rgba(173,216,230,0.5)'),
                name='Bollinger Upper',
                showlegend=False
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=df['Open Time'],
                y=df['Bollinger_Lower'],
                line=dict(color='rgba(173,216,230,0.5)'),
                fill='tonexty',
                fillcolor='rgba(173,216,230,0.2)',
                name='Bollinger Lower',
                showlegend=False
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=df['Open Time'],
                y=df['Bollinger_Middle'],
                line=dict(color='blue', width=1),
                name='Bollinger Middle',
                showlegend=False
            ), row=1, col=1)

        if 'Ichimoku_Cloud' in selected_elements:
            fig.add_trace(go.Scatter(
                x=df['Open Time'],
                y=df['Ichimoku_A'],
                line=dict(color='rgba(255, 0, 0, 0.5)'),
                name='Ichimoku A',
                showlegend=False
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=df['Open Time'],
                y=df['Ichimoku_B'],
                line=dict(color='rgba(0, 255, 0, 0.5)'),
                fill='tonexty',
                fillcolor='rgba(255, 255, 0, 0.2)',
                name='Ichimoku B',
                showlegend=False
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=df['Open Time'],
                y=df['Ichimoku_Base_Line'],
                line=dict(color='blue', width=1),
                name='Ichimoku Base Line',
                showlegend=False
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=df['Open Time'],
                y=df['Ichimoku_Conversion_Line'],
                line=dict(color='orange', width=1),
                name='Ichimoku Conversion Line',
                showlegend=False
            ), row=1, col=1)

        if 'Parabolic_SAR' in selected_elements:
            fig.add_trace(go.Scatter(
                x=df['Open Time'],
                y=df['Parabolic_SAR'],
                mode='markers',
                marker=dict(color='blue', size=3, symbol='circle'),
                name='Parabolic SAR',
                showlegend=False
            ), row=1, col=1)

        if 'VWAP' in selected_elements:
            fig.add_trace(go.Scatter(
                x=df['Open Time'],
                y=df['VWAP'],
                line=dict(color='orange', width=1),
                name='VWAP',
                showlegend=False
            ), row=1, col=1)

        if 'Moving_Average_Envelopes' in selected_elements:
            fig.add_trace(go.Scatter(
                x=df['Open Time'],
                y=df['Moving_Average_Envelope_Upper'],
                line=dict(color='green', width=1),
                name='MA Envelope Upper',
                showlegend=False
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=df['Open Time'],
                y=df['Moving_Average_Envelope_Lower'],
                line=dict(color='green', width=1),
                fill='tonexty',
                fillcolor='rgba(0,255,0,0.2)',
                name='MA Envelope Lower',
                showlegend=False
            ), row=1, col=1)

        if 'support_resistance_levels' in selected_elements:
            supports = analysis_data.get('support_resistance_levels', {}).get('supports', [])
            resistances = analysis_data.get('support_resistance_levels', {}).get('resistances', [])

            for level in supports:
                fig.add_trace(go.Scatter(
                    x=[level['date'], df['Open Time'].iloc[-1]],
                    y=[level['level'], level['level']],
                    mode='lines',
                    line=dict(color='green', dash='dash'),
                    name='Support',
                    showlegend=False
                ), row=1, col=1)

            for level in resistances:
                fig.add_trace(go.Scatter(
                    x=[level['date'], df['Open Time'].iloc[-1]],
                    y=[level['level'], level['level']],
                    mode='lines',
                    line=dict(color='red', dash='dash'),
                    name='Resistance',
                    showlegend=False
                ), row=1, col=1)

        if 'trend_lines' in selected_elements:
            lines = analysis_data.get('trend_lines', {}).get('lines', [])
            for line in lines:
                start_date = line['start_point']['date']
                end_date = line['end_point']['date']
                start_price = line['start_point']['price']
                end_price = line['end_point']['price']

                fig.add_trace(go.Scatter(
                    x=[start_date, end_date],
                    y=[start_price, end_price],
                    mode='lines',
                    line=dict(color='blue', width=2),
                    name='Trend Line',
                    showlegend=False
                ), row=1, col=1)

        if 'unfinished_zones' in selected_elements:
            zones = analysis_data.get('unfinished_zones', [])
            for zone in zones:
                date = zone['date']
                price = zone['level']
                fig.add_trace(go.Scatter(
                    x=[date],
                    y=[price],
                    mode='markers',
                    marker=dict(color='purple', size=10, symbol='star'),
                    name='Unfinished Zone',
                    showlegend=False
                ), row=1, col=1)

        if 'imbalances' in selected_elements:
            imbalances = analysis_data.get('imbalances', [])
            for imbalance in imbalances:
                start_date = imbalance['start_point']['date']
                end_date = imbalance['end_point']['date']
                start_price = imbalance['start_point']['price']
                end_price = imbalance['end_point']['price']

                fig.add_shape(
                    type="rect",
                    x0=start_date,
                    y0=min(start_price, end_price),
                    x1=end_date,
                    y1=max(start_price, end_price),
                    fillcolor="orange",
                    opacity=0.3,
                    line=dict(color="orange", width=1),
                    layer="below"
                )

        if 'fibonacci_analysis' in selected_elements:
            fibonacci_data = analysis_data.get('fibonacci_analysis', {})
            for key in ['based_on_global_trend']:
                fib = fibonacci_data.get(key, {})
                if fib:
                    levels = fib.get('levels', {})
                    start_date = fib.get('start_point', {}).get('date')
                    end_date = fib.get('end_point', {}).get('date')

                    for level_name, price in levels.items():
                        fig.add_trace(go.Scatter(
                            x=[start_date, end_date],
                            y=[price, price],
                            mode='lines',
                            line=dict(color='purple', dash='dash'),
                            name=f"Fibonacci {level_name}",
                            showlegend=False
                        ), row=1, col=1)

        if 'fibonacci_analysis' in selected_elements:
            fibonacci_data = analysis_data.get('fibonacci_analysis', {})
            for key in ['based_on_local_trend']:
                fib = fibonacci_data.get(key, {})
                if fib:
                    levels = fib.get('levels', {})
                    start_date = fib.get('start_point', {}).get('date')
                    end_date = fib.get('end_point', {}).get('date')

                    for level_name, price in levels.items():
                        fig.add_trace(go.Scatter(
                            x=[start_date, end_date],
                            y=[price, price],
                            mode='lines',
                            line=dict(color='green', dash='dash'),
                            name=f"Fibonacci {level_name}",
                            showlegend=False
                        ), row=1, col=1)

        if 'elliott_wave_analysis' in selected_elements:
            waves = analysis_data.get('elliott_wave_analysis', {}).get('waves', [])
            for wave in waves:
                start_date = wave['start_point']['date']
                end_date = wave['end_point']['date']
                start_price = wave['start_point']['price']
                end_price = wave['end_point']['price']
                wave_number = wave['wave_number']
                fig.add_trace(go.Scatter(
                    x=[start_date, end_date],
                    y=[start_price, end_price],
                    mode='lines+markers+text',
                    text=[f"{wave_number}", ""],
                    textposition='top center',
                    line=dict(color='green'),
                    name=f"Wave {wave_number}",
                    showlegend=False
                ), row=1, col=1)

        if 'structural_edge' in selected_elements:
            edges = analysis_data.get('structural_edge', [])
            for edge in edges:
                date = edge['date']
                price = edge['price']
                fig.add_trace(go.Scatter(
                    x=[date],
                    y=[price],
                    mode='markers',
                    marker=dict(color='cyan', size=10, symbol='diamond'),
                    name='Structural Edge',
                    showlegend=False
                ), row=1, col=1)

        if 'candlestick_patterns' in selected_elements:
            patterns = analysis_data.get('candlestick_patterns', [])
            for pattern in patterns:
                date = pattern['date']
                price = pattern['price']
                ptype = pattern.get('type', '')
                symbol = 'circle'
                color = 'magenta'
                if 'bullish' in ptype.lower() or ptype in ['Hammer']:
                    symbol = 'triangle-up'
                    color = 'green'
                elif 'bearish' in ptype.lower() or ptype in ['Shooting Star']:
                    symbol = 'triangle-down'
                    color = 'red'

                fig.add_trace(go.Scatter(
                    x=[date],
                    y=[price],
                    mode='markers',
                    marker=dict(color=color, size=10, symbol=symbol),
                    name='Candlestick Pattern',
                    showlegend=False
                ), row=1, col=1)

        if 'divergence_analysis' in selected_elements:
            divergences = analysis_data.get('divergence_analysis', [])
            for divergence in divergences:
                date = divergence['date']
                dtype = divergence.get('type', '')
                price = None
                if date in df['Open Time'].values:
                    price = df.loc[df['Open Time'] == date, 'Close'].values[0]
                else:
                    continue
                symbol = 'arrow-up' if 'bullish' in dtype else 'arrow-down'
                fig.add_trace(go.Scatter(
                    x=[date],
                    y=[price],
                    mode='markers',
                    marker=dict(color='red', size=12, symbol=symbol),
                    name='Divergence',
                    showlegend=False
                ), row=1, col=1)

        if 'fair_value_gaps' in selected_elements:
            fv_gaps = analysis_data.get('fair_value_gaps', [])
            for fvg in fv_gaps:
                date = fvg['date']
                price_range = fvg['price_range']
                fig.add_shape(
                    type="rect",
                    x0=date,
                    y0=min(price_range),
                    x1=date,
                    y1=max(price_range),
                    fillcolor="cyan",
                    opacity=0.3,
                    line=dict(color="cyan", width=1),
                    layer="below"
                )

        if 'gap_analysis' in selected_elements:
            gaps = analysis_data.get('gap_analysis', {}).get('gaps', [])
            for gap in gaps:
                date = gap['date']
                price_range = gap['price_range']
                fig.add_shape(
                    type="rect",
                    x0=date,
                    y0=min(price_range),
                    x1=date,
                    y1=max(price_range),
                    fillcolor="pink",
                    opacity=0.3,
                    line=dict(color="pink", width=1),
                    layer="below"
                )

        if 'psychological_levels' in selected_elements:
            levels = analysis_data.get('psychological_levels', {}).get('levels', [])
            for level in levels:
                date = level['date']
                price = level['level']
                fig.add_trace(go.Scatter(
                    x=[date, df['Open Time'].iloc[-1]],
                    y=[price, price],
                    mode='lines',
                    line=dict(color='brown', dash='dot'),
                    name='Psychological Level',
                    showlegend=False
                ), row=1, col=1)

        if 'anomalous_candles' in selected_elements:
            candles = analysis_data.get('anomalous_candles', [])
            for candle in candles:
                date = candle['date']
                price = candle['price']
                fig.add_trace(go.Scatter(
                    x=[date],
                    y=[price],
                    mode='markers',
                    marker=dict(color='magenta', size=10, symbol='x'),
                    name='Anomalous Candle',
                    showlegend=False
                ), row=1, col=1)

        if 'price_prediction' in selected_elements:
            virtual_candles = analysis_data.get('price_prediction', {}).get('virtual_candles', [])
            if virtual_candles:
                df_virtual = pd.DataFrame(virtual_candles)
                fig.add_trace(go.Candlestick(
                    x=df_virtual['date'],
                    open=df_virtual['open'],
                    high=df_virtual['high'],
                    low=df_virtual['low'],
                    close=df_virtual['close'],
                    name='Forecast',
                    increasing_line_color='pink',
                    decreasing_line_color='pink',
                    showlegend=False
                ), row=1, col=1)

        if 'recommendations' in selected_elements:
            strategies = analysis_data.get('recommendations', {}).get('trading_strategies', [])
            for strategy in strategies:
                entry_point = strategy.get('entry_point', {})
                exit_point = strategy.get('exit_point', {})
                entry_date = entry_point.get('Date')
                entry_price = entry_point.get('Price')
                exit_date = exit_point.get('Date')
                exit_price = exit_point.get('Price')

                fig.add_trace(go.Scatter(
                    x=[entry_date],
                    y=[entry_price],
                    mode='markers',
                    marker=dict(color='green', size=12, symbol='triangle-up'),
                    name='Entry Point',
                    showlegend=False
                ), row=1, col=1)

                fig.add_trace(go.Scatter(
                    x=[exit_date],
                    y=[exit_price],
                    mode='markers',
                    marker=dict(color='red', size=12, symbol='triangle-down'),
                    name='Exit Point',
                    showlegend=False
                ), row=1, col=1)

        row = 2
        for indicator in indicators_with_subplots:
            if indicator == 'MACD':
                fig.add_trace(go.Scatter(
                    x=df['Open Time'],
                    y=df['MACD'],
                    line=dict(color='blue', width=1),
                    name='MACD',
                    showlegend=False
                ), row=row, col=1)
                fig.add_trace(go.Scatter(
                    x=df['Open Time'],
                    y=df['MACD_signal'],
                    line=dict(color='orange', width=1),
                    name='MACD Signal',
                    showlegend=False
                ), row=row, col=1)
                fig.add_trace(go.Bar(
                    x=df['Open Time'],
                    y=df['MACD_hist'],
                    marker_color='green',
                    name='MACD Histogram',
                    showlegend=False
                ), row=row, col=1)
                row += 1

            elif indicator == 'RSI':
                fig.add_trace(go.Scatter(
                    x=df['Open Time'],
                    y=df['RSI'],
                    line=dict(color='purple', width=1),
                    name='RSI',
                    showlegend=False
                ), row=row, col=1)
                row += 1

            elif indicator == 'OBV':
                fig.add_trace(go.Scatter(
                    x=df['Open Time'],
                    y=df['OBV'],
                    line=dict(color='orange', width=1),
                    name='OBV',
                    showlegend=False
                ), row=row, col=1)
                row += 1

            elif indicator == 'ATR':
                fig.add_trace(go.Scatter(
                    x=df['Open Time'],
                    y=df['ATR'],
                    line=dict(color='green', width=1),
                    name='ATR',
                    showlegend=False
                ), row=row, col=1)
                row += 1

            elif indicator == 'ADX':
                fig.add_trace(go.Scatter(
                    x=df['Open Time'],
                    y=df['ADX'],
                    line=dict(color='brown', width=1),
                    name='ADX',
                    showlegend=False
                ), row=row, col=1)
                row += 1

            elif indicator == 'Stochastic_Oscillator':
                fig.add_trace(go.Scatter(
                    x=df['Open Time'],
                    y=df['Stochastic_Oscillator'],
                    line=dict(color='blue', width=1),
                    name='Stochastic Oscillator',
                    showlegend=False
                ), row=row, col=1)
                row += 1

            elif indicator == 'Volume':
                fig.add_trace(go.Bar(
                    x=df['Open Time'],
                    y=df['Volume'],
                    marker_color='gray',
                    name='Volume',
                    showlegend=False
                ), row=row, col=1)
                row += 1

        fig.update_layout(
            xaxis_rangeslider_visible=False,
            template='plotly_dark',
            height=450 + (num_rows - 0.5) * 100,
            dragmode='pan'
        )

        return fig

    except Exception as e:
        logger.exception(f"Ошибка при создании графика: {e}")
        return go.Figure()


def prepare_explanations(selected_elements: List[str], analysis_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Подготавливает объяснения для выбранных элементов."""
    explanations = []
    validate_analysis(analysis_data)
    try:
        for element in selected_elements:
            # Обработка текстовых объяснений
            if element == 'primary_analysis':
                text = analysis_data.get('primary_analysis', {})
                explanations.append({
                    'Название': 'Первичный анализ',
                    'Текст': '\n'.join(text.values()),
                    'key': element,
                })
            elif element == 'confidence_in_trading_decisions':
                text = analysis_data.get('confidence_in_trading_decisions', {})
                explanations.append({
                    'Название': 'Уверенность в торговых решениях',
                    'Текст': '\n'.join(text.values()),
                    'key': element,
                })
            elif element == 'indicator_correlations':
                correlations = analysis_data.get('indicator_correlations', {})
                text = ''
                for key, value in correlations.items():
                    text += f"{value}\n"
                explanations.append({
                    'Название': 'Indicator Correlations',
                    'Текст': text,
                    'key': element,
                })
            elif element == 'volatility_by_intervals':
                volatility = analysis_data.get('volatility_by_intervals', {})
                text = ''
                for key, value in volatility.items():
                    if isinstance(value, dict):
                        text += f"{key}: {value.get('average_volatility', '')} {value.get('comment', '')}\n"
                    else:
                        text += f"{value}\n"
                explanations.append({
                    'Название': 'Volatility By Intervals',
                    'Текст': text,
                    'key': element,
                })
            elif element == 'market_cycles_identification':
                cycles = analysis_data.get('market_cycles_identification', {})
                text = ''
                for key, value in cycles.items():
                    text += f"{key}: {value}\n"
                explanations.append({
                    'Название': 'Market Cycles Identification',
                    'Текст': text,
                    'key': element,
                })
            elif element == 'extended_ichimoku_analysis':
                ichimoku = analysis_data.get('extended_ichimoku_analysis', {})
                text = ''
                cb_cross = ichimoku.get('conversion_base_line_cross', {})
                text += f"Conversion_base_line_cross: {cb_cross.get('date', '')} {cb_cross.get('signal', '')} : {cb_cross.get('explanation', '')}\n\n"
                pvc = ichimoku.get('price_vs_cloud', {})
                text += f"Price_vs_cloud: {pvc.get('position', '')} {pvc.get('explanation', '')}\n"
                explanations.append({
                    'Название': 'Extended Ichimoku Analysis',
                    'Текст': text,
                    'key': element,
                })
            elif element == 'support_resistance_levels':
                levels = analysis_data.get('support_resistance_levels', {})
                text = ''
                for support in levels.get('supports', []):
                    text += f"supports {support['level']} {support['date']} {support.get('explanation', '')}\n"
                for resistance in levels.get('resistances', []):
                    text += f"resistances {resistance['level']} {resistance['date']} {resistance.get('explanation', '')}\n"
                explanations.append({
                    'Название': 'Уровни поддержки и сопротивления',
                    'Текст': text,
                    'key': element,
                })
            elif element == 'fibonacci_analysis':
                fib = analysis_data.get('fibonacci_analysis', {})
                explanation = ''
                for key in fib.keys():
                    explanation += fib[key].get('explanation', '') + '\n'
                explanations.append({
                    'Название': 'Fibonacci Levels',
                    'Текст': explanation,
                    'key': element,
                })
            elif element == 'elliott_wave_analysis':
                ewa = analysis_data.get('elliott_wave_analysis', {})
                text = f"{ewa.get('current_wave', '')}\n"
                text += f"wave_count: {ewa.get('wave_count', '')}\n"
                text += f"forecast: {ewa.get('forecast', '')}\n"
                text += f"explanation: {ewa.get('explanation', '')}\n"
                explanations.append({
                    'Название': 'Elliott Waves',
                    'Текст': text,
                    'key': element,
                })
            elif element == 'imbalances':
                imbalances = analysis_data.get('imbalances', [])
                text = ''
                for imbalance in imbalances:
                    text += f"{imbalance.get('type', '')} {imbalance.get('start_point', {}).get('price', '')} {imbalance.get('start_point', {}).get('date', '')} {imbalance.get('explanation', '')}\n"
                explanations.append({
                    'Название': 'Imbalances',
                    'Текст': text,
                    'key': element,
                })
            elif element == 'unfinished_zones':
                zones = analysis_data.get('unfinished_zones', [])
                text = ''
                for zone in zones:
                    text += f"{zone.get('type', '')} {zone.get('level', '')} {zone.get('date', '')} {zone.get('explanation', '')}\n"
                explanations.append({
                    'Название': 'Unfinished Zones',
                    'Текст': text,
                    'key': element,
                })
            elif element == 'divergence_analysis':
                divergences = analysis_data.get('divergence_analysis', [])
                text = ''
                for divergence in divergences:
                    text += f"{divergence.get('indicator', '')} {divergence.get('type', '')} {divergence.get('date', '')} {divergence.get('explanation', '')}\n"
                explanations.append({
                    'Название': 'Divergence Analysis',
                    'Текст': text,
                    'key': element,
                })
            elif element == 'structural_edge':
                edges = analysis_data.get('structural_edge', [])
                text = ''
                for edge in edges:
                    text += f"{edge.get('type', '')} {edge.get('date', '')} {edge.get('price', '')} {edge.get('explanation', '')}\n"
                explanations.append({
                    'Название': 'Structural Edge',
                    'Текст': text,
                    'key': element,
                })
            elif element == 'candlestick_patterns':
                patterns = analysis_data.get('candlestick_patterns', [])
                text = ''
                for pattern in patterns:
                    text += f"{pattern.get('type', '')} {pattern.get('explanation', '')}\n"
                explanations.append({
                    'Название': 'Candlestick Patterns',
                    'Текст': text,
                    'key': element,
                })
            elif element == 'gap_analysis':
                gaps = analysis_data.get('gap_analysis', {}).get('gaps', [])
                text = ''
                for gap in gaps:
                    text += f"{gap.get('gap_type', '')} {gap.get('date', '')} {gap.get('explanation', '')}\n"
                explanations.append({
                    'Название': 'Gaps',
                    'Текст': text,
                    'key': element,
                })
            elif element == 'fair_value_gaps':
                fv_gaps = analysis_data.get('fair_value_gaps', [])
                text = ''
                for fvg in fv_gaps:
                    text += f"Date: {fvg.get('date', '')} Explanation: {fvg.get('explanation', '')}\n"
                explanations.append({
                    'Название': 'Fair Value Gaps',
                    'Текст': text,
                    'key': element,
                })
            elif element == 'psychological_levels':
                levels = analysis_data.get('psychological_levels', {}).get('levels', [])
                text = ''
                for level in levels:
                    text += f"{level.get('level', '')} {level.get('date', '')} {level.get('type', '')} {level.get('explanation', '')}\n"
                explanations.append({
                    'Название': 'Psychological Levels',
                    'Текст': text,
                    'key': element,
                })
            elif element == 'anomalous_candles':
                candles = analysis_data.get('anomalous_candles', [])
                text = ''
                for candle in candles:
                    text += f"{candle.get('date', '')} {candle.get('type', '')} {candle.get('explanation', '')}\n"
                explanations.append({
                    'Название': 'Anomalous Candles',
                    'Текст': text,
                    'key': element,
                })
            elif element == 'price_prediction':
                prediction = analysis_data.get('price_prediction', {})
                text = prediction.get('forecast', '')
                explanations.append({
                    'Название': 'Price Prediction',
                    'Текст': text,
                    'key': element,
                })
            elif element == 'recommendations':
                recommendations = analysis_data.get('recommendations', {}).get('trading_strategies', [])
                text = ''
                for rec in recommendations:
                    text += f"strategy: {rec.get('strategy', '')}\n"
                    entry = rec.get('entry_point', {})
                    exit = rec.get('exit_point', {})
                    text += f"вход: Price {entry.get('Price', '')} Date {entry.get('Date', '')}\n"
                    text += f"выход: Price {exit.get('Price', '')} Date {exit.get('Date', '')}\n"
                    text += f"stop_loss: {rec.get('stop_loss', '')}\n"
                    text += f"take_profit: {rec.get('take_profit', '')}\n"
                    text += f"risk: {rec.get('risk', '')}\n"
                    text += f"other_details: {rec.get('other_details', '')}\n\n"
                explanations.append({
                    'Название': 'Recommendations',
                    'Текст': text,
                    'key': element,
                })
            elif element == 'volume':
                volume_analysis = analysis_data.get('volume_analysis', {})
                text = volume_analysis.get('volume_trends', '') + '\n'
                significant_changes = volume_analysis.get('significant_volume_changes', [])
                for change in significant_changes:
                    text += f"{change.get('date', '')} {change.get('price', '')} {change.get('volume', '')} {change.get('explanation', '')}\n"
                explanations.append({
                    'Название': 'Volume',
                    'Текст': text,
                    'key': element,
                })
            # Обработка базовых индикаторов
            elif element in ['RSI', 'MACD', 'OBV', 'ATR', 'ADX']:
                indicators = analysis_data.get('indicators_analysis', {})
                data = indicators.get(element, {})
                current_value = data.get('current_value', '')
                comment = data.get('comment', '')
                text = f"{element} {current_value} {comment}"
                explanations.append({
                    'Название': element,
                    'Текст': text,
                    'key': element,
                })
            # Обработка продвинутых индикаторов
            elif element in ['Bollinger_Bands', 'Ichimoku_Cloud', 'Parabolic_SAR', 'VWAP', 'Moving_Average_Envelopes']:
                indicators = analysis_data.get('indicators_analysis', {})
                data = indicators.get(element, {})
                trend = data.get('trend', '')
                comment = data.get('comment', '')
                text = f"{element} {trend} {comment}"
                explanations.append({
                    'Название': element,
                    'Текст': text,
                    'key': element,
                })

            else:
                # Для других элементов можно добавить соответствующую обработку
                pass
        return explanations
    except Exception as e:
        logger.exception(f"Ошибка при подготовке объяснений: {e}")
        return explanations
