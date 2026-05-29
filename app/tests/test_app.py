import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


def test_index_returns_200(client):
    response = client.get('/')
    assert response.status_code == 200


def test_index_contains_status(client):
    response = client.get('/')
    data = response.get_json()
    assert data['status'] == 'ok'


def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'healthy'


def test_ready_endpoint(client):
    response = client.get('/ready')
    assert response.status_code == 200


def test_api_data_returns_items(client):
    response = client.get('/api/data')
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
    assert len(data['items']) == 3


def test_error_endpoint_returns_500(client):
    response = client.get('/api/error')
    assert response.status_code == 500


def test_metrics_endpoint(client):
    response = client.get('/metrics')
    assert response.status_code == 200
    assert b'http_requests_total' in response.data


def test_404_handler(client):
    response = client.get('/nicht-vorhanden')
    assert response.status_code == 404
