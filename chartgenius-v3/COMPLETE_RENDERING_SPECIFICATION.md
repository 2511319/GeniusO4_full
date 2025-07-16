# ChartGenius v3 - Полная спецификация рендеринга элементов

## Основано на реальной структуре ответа модели

**Источник данных**: `GeniusO4_full-stable/backend/invalid_llm_response_1751918388.txt`

## КРИТИЧЕСКИЕ СТАНДАРТЫ ВИЗУАЛИЗАЦИИ

### 1. risk_management - Таблица с иконками
- **Расположение**: Верх правой панели (всегда видимая)
- **Цвет**: Красный градиент (от red-900 до red-800)
- **Иконки**: Shield, AlertTriangle, CheckCircle

### 2. support_resistance_levels - ЛУЧИ (не горизонтальные линии)
- **Визуализация**: Луч начинается в точке level/date и продолжается вправо
- **Поддержка**: Зеленые лучи (#22c55e) с маркером arrowUp
- **Сопротивление**: Красные лучи (#ef4444) с маркером arrowDown

### 3. fibonacci_analysis - Прямоугольные области
- **Визуализация**: Прямоугольник от start_point до end_point
- **Уровни**: Горизонтальные пунктирные линии внутри прямоугольника
- **Цвет**: Желтый (#ffc107) с прозрачностью

### 4. volume_analysis - Столбцы под свечами
- **Визуализация**: Гистограмма объемов под основным графиком
- **Цвет**: Зеленый для высоких объемов, стандартный для обычных
- **Маркеры**: Желтые круги для значительных изменений

## СТРУКТУРА ДАННЫХ МОДЕЛИ

### Геометрические элементы с start_point/end_point:
```json
{
  "imbalances": [
    {
      "start_point": {"date": "2025-07-07 01:00:00", "price": 108740},
      "end_point": {"date": "2025-07-07 02:00:00", "price": 108900},
      "explanation": "Дисбаланс между спросом и предложением..."
    }
  ],
  "trend_lines": [
    {
      "start_point": {"date": "2025-07-06 20:00:00", "price": 107500},
      "end_point": {"date": "2025-07-07 10:00:00", "price": 109000},
      "explanation": "Восходящая линия тренда..."
    }
  ],
  "fibonacci_analysis": {
    "based_on_local_trend": {
      "start_point": {"date": "2025-07-01 20:00:00", "price": 105918.54},
      "end_point": {"date": "2025-07-07 10:00:00", "price": 109839},
      "levels": {
        "0%": 107500,
        "23.6%": 108100,
        "50%": 108300,
        "61.8%": 109000,
        "100%": 110000
      }
    }
  },
  "elliott_wave_analysis": {
    "waves": [
      {
        "wave_number": 1,
        "start_point": {"date": "2025-07-06 20:00:00", "price": 107500},
        "end_point": {"date": "2025-07-06 22:00:00", "price": 108200}
      }
    ]
  }
}
```

### Уровни с координатами:
```json
{
  "support_resistance_levels": {
    "supports": [
      {
        "level": 107900,
        "date": "2025-07-06 22:00:00",
        "explanation": "Тестировавшийся уровень...",
        "ray_slope": "upward"
      }
    ],
    "resistances": [
      {
        "level": 109500,
        "date": "2025-07-06 21:00:00",
        "explanation": "Ранее протестированный уровень...",
        "ray_slope": "downward"
      }
    ]
  },
  "unfinished_zones": [
    {
      "level": 108500,
      "date": "2025-07-07 00:00:00",
      "line_style": "dashed",
      "line_color": "orange",
      "explanation": "Незавершенная зона..."
    }
  ],
  "psychological_levels": [
    {
      "level": 108000,
      "date": "2025-07-07 00:00:00",
      "type": "round_number",
      "explanation": "Психологический уровень..."
    }
  ]
}
```

### Свечные данные:
```json
{
  "price_prediction": {
    "virtual_candles": [
      {
        "date": "2025-07-08 00:00:00",
        "open": 108200,
        "high": 108800,
        "low": 108000,
        "close": 108700
      }
    ]
  },
  "candlestick_patterns": [
    {
      "date": "2025-07-07 01:00:00",
      "type": "doji",
      "price": 108740,
      "explanation": "Паттерн доджи указывает на неопределенность..."
    }
  ],
  "anomalous_candles": [
    {
      "date": "2025-07-07 01:00:00",
      "type": "long_wick",
      "price": 108740,
      "explanation": "Длинный фитиль указывает на отклонение..."
    }
  ]
}
```

### Индикаторы и анализ:
```json
{
  "indicators_analysis": {
    "rsi": {"value": 65.2, "signal": "neutral"},
    "macd": {"value": 0.15, "signal": "bullish"},
    "bollinger_bands": {
      "upper": 109200,
      "middle": 108500,
      "lower": 107800,
      "signal": "neutral"
    },
    "moving_averages": {
      "sma_20": 108300,
      "sma_50": 107900,
      "ema_12": 108400,
      "ema_26": 108100
    }
  },
  "volume_analysis": {
    "volume_trends": "Объемы торговли остаются высокими...",
    "significant_volume_changes": [
      {
        "date": "2025-07-07 01:00:00",
        "price": 108740,
        "volume": 2300,
        "explanation": "Значительное изменение объема..."
      }
    ]
  },
  "divergence_analysis": [
    {
      "type": "bullish",
      "indicator": "RSI",
      "date": "2025-07-07 00:00:00",
      "explanation": "Бычья дивергенция между ценой и RSI..."
    }
  ]
}
```

## ПРИОРИТЕТЫ РЕНДЕРИНГА

### Группа 1: ТОРГОВЫЕ РЕШЕНИЯ (Критический приоритет)
1. **risk_management** - Таблица с иконками (всегда видимая)
2. **confidence_in_trading_decisions** - Шкала уверенности
3. **price_prediction** - Виртуальные свечи + панель прогноза

### Группа 2: КЛЮЧЕВЫЕ ИНДИКАТОРЫ
4. **volume_analysis** - Столбцы под свечами
5. **indicators_analysis** - Панель индикаторов
6. **divergence_analysis** - Маркеры дивергенций

### Группа 3: УРОВНИ И СТРУКТУРА
7. **support_resistance_levels** - Лучи (не линии!)
8. **fibonacci_analysis** - Прямоугольные области
9. **trend_lines** - Линии тренда
10. **unfinished_zones** - Пунктирные уровни

### Группа 4: ВОЛНОВОЙ И ФИБОНАЧЧИ АНАЛИЗ
11. **elliott_wave_analysis** - Волновая разметка
12. **imbalances** - Прямоугольники дисбалансов

### Группа 5: ПАТТЕРНЫ И АНОМАЛИИ
13. **candlestick_patterns** - Маркеры паттернов
14. **anomalous_candles** - Выделение аномальных свечей
15. **psychological_levels** - Психологические уровни

## ЦВЕТОВАЯ СХЕМА

- **Поддержка**: #22c55e (зеленый)
- **Сопротивление**: #ef4444 (красный)
- **Фибоначчи**: #ffc107 (желтый)
- **Объемы**: #26a69a (бирюзовый)
- **Риски**: red-900 до red-800 (градиент)
- **Нейтральные элементы**: gray-600 до gray-800

## ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ

1. **Lightweight Charts**: Основная библиотека для рендеринга
2. **React + Tailwind CSS**: UI фреймворк
3. **Responsive Design**: Адаптивность под разные экраны
4. **Real-time Updates**: Обновление данных в реальном времени
5. **Interactive Elements**: Hover эффекты и кликабельные элементы
