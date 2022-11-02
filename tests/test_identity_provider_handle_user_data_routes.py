from fastapi.testclient import TestClient
from fastapi import status
from decouple import config
from modules.jwt.jwt_module import JwtEncoder
from main import app

def test_delete_user_endpoint_invalid_password():
    #ARRANGE
    VALID_TOKEN=config("VALID_TOKEN")
    client = TestClient(app)
    del_user = {
          "token": VALID_TOKEN
    }
    expected_error = {
        "detail":"Invalid password"
    }
    #ACT
    response = client.delete("/users", json={"password":"invalid"}, headers=del_user)
    #ASSERT
    assert response.status_code == 403
    assert response.json() == expected_error


def test_delete_user_endpoint_success():
    #ARRANGE
    client = TestClient(app)
    test_user = {
        "first_name":"test",
        "last_name":"test",
        "user_name":"test_usr2",
        "email":"test@test.com",
        "password":"testtesttest4"
    }
    new_user = client.post("/users",json=test_user)
    del_user = {
          "token": new_user.json()["token"]
    }
    #ACT
    response = client.delete("/users", json={"password":"testtesttest4"}, headers=del_user)
    #ASSERT
    assert response.status_code == 204