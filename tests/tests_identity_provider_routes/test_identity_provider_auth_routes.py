from fastapi.testclient import TestClient
from fastapi import status
from decouple import config
from modules.jwt.jwt_module import JwtEncoder
from main import app

def test_login_user_endpoint_success():
    #ARRANGE
    client = TestClient(app)
    test_user = {
        "user_name":"test_usr",
        "password":"testtesttest4"
    }
    #ACT
    response = client.post("/login",json=test_user)
    #ASSERT
    assert response.status_code == 200
    assert "token" in response.json()
    assert response.json()["userName"] == "test_usr"


def test_login_user_endpoint_fails_invalid_credentials():
    #ARRANGE
    client = TestClient(app)
    test_user = {
        "user_name":"test_usr",
        "password":"testtesttest1"
    }
    #ACT
    response = client.post("/login",json=test_user)
    #ASSERT
    assert response.status_code == 403
    assert response.json() == {'detail': 'Invalid credentials'}
