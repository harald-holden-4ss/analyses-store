from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from dotenv import load_dotenv

import os
import pytest

db_serv_mock = MagicMock() 

@pytest.fixture
def app():
    load_dotenv()
    os.environ['ENVIRONMENT'] = 'development'
    from app.fast_api_app import get_app
    app = get_app(db_serv=db_serv_mock)
    return app


def test_pingpong(app):
    client = TestClient(app)
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == "pong"


def test_get_user(app):
    client = TestClient(app)
    response = client.get("/user")
    assert response.status_code == 200
    assert response.json() == {
        'name': 'John Doe', 
        'email': 'john@doe.com',
        'organizationId': '2c4ee562-6261-4018-a1b1-8837ab526944'}

def test_get_vessels(app):
    client = TestClient(app)
    response = client.get("/vessels")
    assert response.status_code == 200
