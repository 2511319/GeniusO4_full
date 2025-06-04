import os
from dash import Dash, dcc, html

# Берём тикер по умолчанию из окружения
DEFAULT_SYMBOL = os.getenv("DEFAULT_SYMBOL", "BTCUSDT")

# Инициализация Dash-приложения
app = Dash(
    __name__,
    suppress_callback_exceptions=True
)

# Разметка страницы
app.layout = html.Div([
    html.H1("ChartGenius"),
    html.Div([
        html.Label("Тикер:"),
        dcc.Input(
            id="symbol-input",
            type="text",
            # по умолчанию BTCUSDT, чтобы не было пустого запроса
            value=DEFAULT_SYMBOL,
            placeholder="Введите тикер, например BTCUSDT"
        ),
    ], style={"margin-bottom": "10px"}),
    html.Div([
        html.Label("Интервал:"),
        dcc.Dropdown(
            id="interval-dropdown",
            options=[
                {"label": "1 минута", "value": "1m"},
                {"label": "5 минут", "value": "5m"},
                {"label": "15 минут", "value": "15m"},
                {"label": "1 час", "value": "1h"},
                {"label": "4 часа", "value": "4h"},
                {"label": "1 день", "value": "1d"},
            ],
            value="1h",
            clearable=False,
        ),
    ], style={"margin-bottom": "10px"}),
    html.Div([
        html.Label("Количество свечей:"),
        dcc.Input(
            id="limit-input",
            type="number",
            value=100,
            min=1
        ),
    ], style={"margin-bottom": "10px"}),
    html.Button("Анализ", id="analyze-button", n_clicks=0),
    html.Hr(),
    dcc.Graph(id="chart"),
    html.Pre(id="analysis", style={"whiteSpace": "pre-wrap"}),
    dcc.Store(id="analysis-store"),
])

# Регистрируем коллбэки
from dash_app.callbacks import register_callbacks
register_callbacks(app)

if __name__ == "__main__":
    port = int(os.getenv("DASH_PORT", 8050))
    debug = os.getenv("DEBUG_LOGGING", "false").lower() == "true"
    # новый вызов
    app.run(debug=debug, port=port)
