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
    response = client.post("/register",json=test_user)
    #ASSERT
    assert response.status_code == 201
    assert "token" in response.cookies
    assert response.json()["userName"] == "test_usr2"
    #CLEANUP
    client.delete("/users", json={"password":"testtesttest4"}, cookies={"token":response.cookies.get("token")})


def test_register_user_creates_favorites_obj_for_user():
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
    register_user_response = client.post("/register",json=test_user)
    auth_token = register_user_response.cookies.get("token")
    get_favorites_obj_response = client.get("/favorites", cookies={"token":auth_token})
    #ASSERT
    assert get_favorites_obj_response.status_code == 200
    assert "componentIds" in get_favorites_obj_response.json()

    #CLEANUP
    client.delete("/users", json={"password":"testtesttest4"}, cookies={"token":auth_token})


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
    response = client.post("/register",json=test_user)
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
    response = client.post("/register",json=test_user)
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
    response = client.post("/register",json=test_user)
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
    response = client.post("/register",json=test_user)
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
    response = client.post("/register",json=test_user)
    #ASSERT
    assert response.status_code == 422