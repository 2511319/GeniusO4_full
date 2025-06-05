from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))
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
