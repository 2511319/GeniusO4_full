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
