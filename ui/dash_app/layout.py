# ui/dash_app/layout.py
from dash import html, dcc
import dash_bootstrap_components as dbc

layout = dbc.Container([

    dbc.Row(dbc.Col(html.H2("GeniusO4 Dashboard"), width=12), className="mt-3"),

    # --- Новая строка ввода параметров ---
    dbc.Row([
        # Тикер как свободный ввод
        dbc.Col([
            dbc.Label("Тикер"),
            dbc.Input(
                id="input-symbol",
                type="text",
                placeholder="Введите тикер, например BTCUSDT",
                value="BTCUSDT"
            )
        ], width=3),

        # Тайм-фрейм, как раньше
        dbc.Col([
            dbc.Label("Тайм-фрейм"),
            dcc.Dropdown(
                id="input-interval",
                options=[
                    {"label":"1m","value":"1m"},
                    {"label":"5m","value":"5m"},
                    {"label":"15m","value":"15m"},
                    {"label":"1h","value":"1h"},
                    {"label":"4h","value":"4h"},
                    {"label":"1d","value":"1d"},
                ],
                value="4h",
                clearable=False
            )
        ], width=3),

        # Поле «Количество свечей»
        dbc.Col([
            dbc.Label("Количество свечей"),
            dbc.Input(
                id="input-limit",
                type="number",
                value=144,
                min=1,
                step=1
            )
        ], width=2),

        # Кнопка «Анализ»
        dbc.Col(
            dbc.Button("Анализ", id="button-analyze", color="primary", className="mt-4"),
            width=2
        ),
    ], className="g-3"),

    # Хранилища состояния
    dcc.Store(id="stored-figure"),
    dcc.Store(id="stored-analysis"),

    # График и вывод модели
    dbc.Row(dbc.Col(dcc.Graph(id="main-chart"), width=12)),
    dbc.Row(dbc.Col(html.Pre(id="analysis-output"), width=12)),

], fluid=True)
