from fastapi.testclient import TestClient
from fastapi import status
from decouple import config
from modules.jwt.jwt_module import JwtEncoder
from main import app


def test_get_user_endpoint_returns_user_data():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN=config("VALID_TOKEN")
    auth_cookie = {
          "token": VALID_TOKEN
    }
    expected_user_data = {
        "firstName":"test",
        "lastName":"test",
        "userName":"test_usr",
        "email":"test@test.com",
    }
    #ACT
    response = client.get(f"/users", cookies=auth_cookie)
    #ASSERT
    assert response.status_code == 200
    assert response.json() == expected_user_data


def test_get_user_endpoint_fails_user_not_found():
    #ARRANGE
    client = TestClient(app)
    JWT_SECRET = config("JWT_SECRET")
    jwt_aud="kbe-aw2022-frontend.netlify.app"
    jwt_iss="cs-identity-provider.deta.dev"
    jwt_encoder = JwtEncoder(JWT_SECRET, "HS256")
    test_user = {
        "first_name":"test",
        "last_name":"test",
        "user_name":"test_usr2",
        "email":"test@test.com",
        "password":"testtesttest4"
    }
    new_user_response = client.post("/register",json=test_user)
    new_user_token = new_user_response.cookies.get("token")
    new_user_id = jwt_encoder.decode_jwt(token=new_user_token,audience=jwt_aud,issuer=jwt_iss)["userId"]
    auth_cookie = {
          "token": new_user_token
    }
    client.delete("/users", json={"password":"testtesttest4"}, cookies=auth_cookie)
    expected_error = {
        "detail": "User not found"
    }

    #ACT
    response = client.get(f"/users", cookies=auth_cookie)
    #ASSERT
    assert response.status_code == 404
    assert response.json() == expected_error


def test_get_user_endpoint_fails_invalid_token():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    auth_cookie = {
          "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI3MDNjN2I2Yi00MDA5LTExZWQtYWRiZS03NzQyY2VmNGI1MDQiLCJleHAiOjE2Njc0NjIzODQuNzY1Njk1fQ.QTGA2c2r2EGZ6hjZ0OPqKuXf9VfHnPuTJDi40tvOfW4"
    }
    expected_error = {
        "detail": "Invalid token"
    }
    #ACT
    response = client.get(f"/users", cookies=auth_cookie)
    #ASSERT
    assert response.status_code == 403
    assert response.json() == expected_error


def test_change_password_endpoint_success():
    #ARRANGE
    client = TestClient(app)
    JWT_SECRET = config("JWT_SECRET")
    jwt_aud="kbe-aw2022-frontend.netlify.app"
    jwt_iss="cs-identity-provider.deta.dev"
    jwt_encoder = JwtEncoder(JWT_SECRET, "HS256")
    test_user = {
        "first_name":"test",
        "last_name":"test",
        "user_name":"test_usr2",
        "email":"test@test.com",
        "password":"testtesttest4"
    }
    test_user_password_update = {
        "password":"testtesttest4",
        "new_password":"testtesttest5"
    }
    new_user_response = client.post("/register",json=test_user)
    new_user_token = new_user_response.cookies.get("token")
    new_user_id = jwt_encoder.decode_jwt(token=new_user_token,audience=jwt_aud,issuer=jwt_iss)["userId"]
    auth_cookie = {
          "token": new_user_token
    }
    #ACT
    response = client.patch(f"/users/password", json=test_user_password_update, cookies=auth_cookie)
    #ASSERT
    assert response.status_code == 204
    #CLEANUP
    client.delete("/users", json={"password":"testtesttest5"}, cookies=auth_cookie)


def test_change_password_endpoint_fails_forbidden_wrong_password():
    #ARRANGE
    client = TestClient(app)
    JWT_SECRET = config("JWT_SECRET")
    jwt_aud="kbe-aw2022-frontend.netlify.app"
    jwt_iss="cs-identity-provider.deta.dev"
    jwt_encoder = JwtEncoder(JWT_SECRET, "HS256")
    test_user = {
        "first_name":"test",
        "last_name":"test",
        "user_name":"test_usr2",
        "email":"test@test.com",
        "password":"testtesttest4"
    }
    test_user_password_update = {
        "password":"invalid_password",
        "new_password":"testtesttest5"
    }
    expected_error = {
        "detail":"Invalid password"
    }
    new_user_response = client.post("/register",json=test_user)
    new_user_token = new_user_response.cookies.get("token")
    new_user_id = jwt_encoder.decode_jwt(token=new_user_token,audience=jwt_aud,issuer=jwt_iss)["userId"]
    auth_cookie = {
          "token": new_user_token
    }
    #ACT
    response = client.patch(f"/users/password", json=test_user_password_update, cookies=auth_cookie)
    #ASSERT
    assert response.status_code == 403
    assert response.json() == expected_error
    #CLEANUP
    client.delete("/users", json={"password":"testtesttest4"}, cookies=auth_cookie)


def test_change_password_endpoint_fails_invalid_token():
    #ARRANGE
    client = TestClient(app)
    JWT_SECRET = config("JWT_SECRET")
    jwt_aud="kbe-aw2022-frontend.netlify.app"
    jwt_iss="cs-identity-provider.deta.dev"
    jwt_encoder = JwtEncoder(JWT_SECRET, "HS256")
    test_user = {
        "first_name":"test",
        "last_name":"test",
        "user_name":"test_usr2",
        "email":"test@test.com",
        "password":"testtesttest4"
    }
    test_user_password_update = {
        "password":"testtesttest4",
        "new_password":"testtesttest5"
    }
    expected_error = {
        "detail":"Invalid token"
    }
    new_user_response = client.post("/register",json=test_user)
    new_user_token = new_user_response.cookies.get("token")
    new_user_id = jwt_encoder.decode_jwt(token=new_user_token,audience=jwt_aud,issuer=jwt_iss)["userId"]
    auth_cookie = {
          "token": "invalid token"
    }
    #ACT
    response = client.patch(f"/users/password", json=test_user_password_update, cookies=auth_cookie)
    #ASSERT
    assert response.status_code == 403
    assert response.json() == expected_error
    #CLEANUP
    client.delete("/users", json={"password":"testtesttest4"}, cookies=auth_cookie)


def test_change_password_endpoint_fails_invalid_new_password():
    #ARRANGE
    client = TestClient(app)
    JWT_SECRET = config("JWT_SECRET")
    jwt_aud="kbe-aw2022-frontend.netlify.app"
    jwt_iss="cs-identity-provider.deta.dev"
    jwt_encoder = JwtEncoder(JWT_SECRET, "HS256")
    test_user = {
        "first_name":"test",
        "last_name":"test",
        "user_name":"test_usr2",
        "email":"test@test.com",
        "password":"testtesttest4"
    }
    test_user_password_update = {
        "password":"testtesttest4",
        "new_password":"invalid_new_password"
    }
    new_user_response = client.post("/register",json=test_user)
    new_user_token = new_user_response.cookies.get("token")
    new_user_id = jwt_encoder.decode_jwt(token=new_user_token,audience=jwt_aud,issuer=jwt_iss)["userId"]
    auth_cookie = {
          "token": new_user_token
    }
    #ACT
    response = client.patch(f"/users/password", json=test_user_password_update, cookies=auth_cookie)
    #ASSERT
    assert response.status_code == 422
    #CLEANUP
    client.delete("/users", json={"password":"testtesttest4"}, cookies=auth_cookie)


def test_change_password_endpoint_fails_user_not_found():
    #ARRANGE
    client = TestClient(app)
    JWT_SECRET = config("JWT_SECRET")
    jwt_aud="kbe-aw2022-frontend.netlify.app"
    jwt_iss="cs-identity-provider.deta.dev"
    jwt_encoder = JwtEncoder(JWT_SECRET, "HS256")
    test_user = {
        "first_name":"test",
        "last_name":"test",
        "user_name":"test_usr2",
        "email":"test@test.com",
        "password":"testtesttest4"
    }
    test_user_password_update = {
        "password":"testtesttest4",
        "new_password":"testtesttest4"
    }
    expected_error = {
        "detail": "User not found"
    }
    new_user_response = client.post("/register",json=test_user)
    new_user_token = new_user_response.cookies.get("token")
    new_user_id = jwt_encoder.decode_jwt(token=new_user_token,audience=jwt_aud,issuer=jwt_iss)["userId"]
    auth_cookie = {
          "token": new_user_token
    }
    client.delete("/users", json={"password":"testtesttest4"}, cookies=auth_cookie)
    #ACT
    response = client.patch(f"/users/password", json=test_user_password_update, cookies=auth_cookie)
    #ASSERT
    assert response.status_code == 404
    assert response.json() == expected_error


def test_delete_user_endpoint_invalid_password():
    #ARRANGE
    VALID_TOKEN=config("VALID_TOKEN")
    client = TestClient(app)
    auth_cookie = {
          "token": VALID_TOKEN
    }
    expected_error = {
        "detail":"Invalid password"
    }
    #ACT
    response = client.delete("/users", json={"password":"invalid"}, cookies=auth_cookie)
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
    new_user_response = client.post("/register",json=test_user)
    new_user_token = new_user_response.cookies.get("token")
    auth_cookie = {
          "token": new_user_token
    }
    #ACT
    response = client.delete("/users", json={"password":"testtesttest4"}, cookies=auth_cookie)
    #ASSERT
    assert response.status_code == 204