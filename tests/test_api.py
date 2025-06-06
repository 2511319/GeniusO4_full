from fastapi.testclient import TestClient
import sys
import os
import pandas as pd
import jwt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))
import app as app_module
from app import app

client = TestClient(app)


def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json() == {'status': 'ok'}


def test_analyze_auth_required():
    payload = {
        'symbol': 'BTCUSDT',
        'interval': '4h',
        'limit': 1,
        'indicators': []
    }
    r = client.post('/api/analyze', json=payload)
    assert r.status_code == 403


def test_analyze_success(monkeypatch):
    token = jwt.encode({'sub': 'tester'}, app_module.SECRET_KEY, algorithm='HS256')

    df = pd.DataFrame({
        'Open Time': pd.date_range('2021-01-01', periods=2, freq='h'),
        'Open': [1, 2],
        'High': [2, 3],
        'Low': [0, 1],
        'Close': [1, 2],
        'Volume': [10, 11],
        'Quote Asset Volume': [10, 11],
        'Number of Trades': [1, 2],
        'Ignore': [0, 0],
        'Taker Buy Base Asset Volume': [5, 6],
        'Taker Buy Quote Asset Volume': [50, 60]
    })

    async def fake_fetch(symbol, interval, limit):
        return df

    def fake_analyze(self, payload):
        return {'summary': 'ok'}

    monkeypatch.setattr('routers.analysis.fetch_ohlcv', fake_fetch)
    monkeypatch.setattr('routers.analysis.ChatGPTAnalyzer.analyze', fake_analyze)

    payload = {
        'symbol': 'BTCUSDT',
        'interval': '4h',
        'limit': 2,
        'indicators': []
    }
    headers = {'Authorization': f'Bearer {token}'}
    r = client.post('/api/analyze', json=payload, headers=headers)
    assert r.status_code == 200
    data = r.json()
    for key in ['figure', 'analysis', 'ohlc', 'indicators']:
        assert key in data

def test_analyze_returns_limit_candles(monkeypatch):
    token = jwt.encode({'sub': 'tester'}, app_module.SECRET_KEY, algorithm='HS256')
    limit = 10
    extra = 200
    fetch_limit = limit + extra
    df = pd.DataFrame({
        'Open Time': pd.date_range('2021-01-01', periods=fetch_limit, freq='h'),
        'Open': range(fetch_limit),
        'High': range(fetch_limit),
        'Low': range(fetch_limit),
        'Close': range(fetch_limit),
        'Volume': range(fetch_limit),
        'Quote Asset Volume': range(fetch_limit),
        'Number of Trades': range(fetch_limit),
        'Ignore': [0]*fetch_limit,
        'Taker Buy Base Asset Volume': range(fetch_limit),
        'Taker Buy Quote Asset Volume': range(fetch_limit)
    })

    async def fake_fetch(symbol, interval, limit_param):
        assert limit_param == fetch_limit
        return df

    class DummyProcessor:
        def __init__(self, _df):
            self.df = _df
        def perform_full_processing(self, drop_na=True):
            return self.df
        def get_ohlc_data(self, num_candles):
            return self.df.tail(num_candles).to_dict(orient='records')

    monkeypatch.setattr('routers.analysis.fetch_ohlcv', fake_fetch)
    monkeypatch.setattr('routers.analysis.DataProcessor', DummyProcessor)
    monkeypatch.setattr('routers.analysis.ChatGPTAnalyzer.analyze', lambda self, payload: {'summary': 'ok'})

    payload = {
        'symbol': 'BTCUSDT',
        'interval': '4h',
        'limit': limit,
        'indicators': []
    }
    headers = {'Authorization': f'Bearer {token}'}
    r = client.post('/api/analyze', json=payload, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data['ohlc']) == limit
    assert data['ohlc'][0]['Open'] == df.iloc[-limit]['Open']
    assert data['ohlc'][-1]['Open'] == df.iloc[-1]['Open']
