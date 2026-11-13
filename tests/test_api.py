import pytest
from ss14tts import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.data.decode() == "OK"

def test_voices(client):
    response = client.get('/voices')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert 'aidar' in data
    assert 'aidar_deep' in data

def test_tts_no_token(client):
    response = client.post('/tts', json={"text": "test", "speaker": "aidar"})
    assert response.status_code == 400
    assert "Missing api_token" in response.get_json()['description']

def test_tts_bad_token(client):
    response = client.post('/tts', json={"text": "test", "speaker": "aidar", "api_token": "wrong"})
    assert response.status_code == 403

def test_tts_success(client):
    payload = {
        "text": "Привет",
        "speaker": "aidar_deep",
        "api_token": "test",
        "format": "wav"
    }
    response = client.post('/tts', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert 'results' in data
    assert 'audio' in data['results'][0]
