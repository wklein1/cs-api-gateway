from fastapi.testclient import TestClient
from fastapi import status
from decouple import config
from main import app


def test_register_user_endpoint_success():
    #ARRANGE
    client = TestClient(app)
    test_user = {
        "first_name":"test",
        "last_name":"test",
        "user_name":"test_usr2",
        "email":"test@test.com",
        "password":"testtesttest4"
    }
    #ACT
    response = client.post("/users",json=test_user)
    #ASSERT
    assert response.status_code == 201
    assert "token" in response.json()
    assert response.json()["userName"] == "test_usr2"
    #CLEANUP
    client.delete("/users", json={"password":"testtesttest4"}, headers={"token":response.json()["token"]})


def test_register_user_endpoint_fails_invalid_password():
    #ARRANGE
    client = TestClient(app)
    test_user = {
        "first_name":"test",
        "last_name":"test",
        "user_name":"test_usr",
        "email":"test@test.com",
        "password":"test"
    }
    #ACT
    response = client.post("/users",json=test_user)
    #ASSERT
    assert response.status_code == 422


def test_register_user_endpoint_fails_invalid_email():
    #ARRANGE
    client = TestClient(app)
    test_user = {
        "first_name":"test",
        "last_name":"test",
        "user_name":"test_usr",
        "email":"testtest.com",
        "password":"testtesttest4"
    }
    #ACT
    response = client.post("/users",json=test_user)
    #ASSERT
    assert response.status_code == 422


def test_register_user_endpoint_fails_invalid_first_name():
    #ARRANGE
    client = TestClient(app)
    test_user = {
        "first_name":"t",
        "last_name":"test",
        "user_name":"test_usr",
        "email":"test@test.com",
        "password":"testtesttest4"
    }
    #ACT
    response = client.post("/users",json=test_user)
    #ASSERT
    assert response.status_code == 422


def test_register_user_endpoint_fails_invalid_last_name():
    #ARRANGE
    client = TestClient(app)
    test_user = {
        "first_name":"test",
        "last_name":"",
        "user_name":"test_usr",
        "email":"test@test.com",
        "password":"testtesttest4"
    }
    #ACT
    response = client.post("/users",json=test_user)
    #ASSERT
    assert response.status_code == 422


def test_register_user_endpoint_fails_invalid_user_name():
    #ARRANGE
    client = TestClient(app)
    test_user = {
        "first_name":"test",
        "last_name":"test",
        "user_name":"",
        "email":"test@test.com",
        "password":"testtesttest4"
    }
    #ACT
    response = client.post("/users",json=test_user)
    #ASSERT
    assert response.status_code == 422