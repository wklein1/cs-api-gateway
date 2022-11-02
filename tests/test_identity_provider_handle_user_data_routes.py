from fastapi.testclient import TestClient
from fastapi import status
from decouple import config
from modules.jwt.jwt_module import JwtEncoder
from main import app

def test_delete_user_endpoint_invalid_password():
    #ARRANGE
    client = TestClient(app)
    del_user = {
          "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJlYmFkMmFlZC01YWU0LTExZWQtYjZhNy02YmExMGJlZTYzOTYiLCJhdWQiOiJrYmUtYXcyMDIyLWZyb250ZW5kLm5ldGxpZnkuYXBwIiwiaXNzIjoiY3MtaWRlbnRpdHktcHJvdmlkZXIuZGV0YS5kZXYiLCJpYXQiOjE2Njc0MTc0NzcuMjAxMzM2LCJleHAiOjE2Njc0MTg2NzguMjAxMzYyfQ.nH-0oHY_74lV_TozZL2ftVxVJclVtolFA_3UsLQox0o"
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
    
    del_user = {
          "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJlYmFkMmFlZC01YWU0LTExZWQtYjZhNy02YmExMGJlZTYzOTYiLCJhdWQiOiJrYmUtYXcyMDIyLWZyb250ZW5kLm5ldGxpZnkuYXBwIiwiaXNzIjoiY3MtaWRlbnRpdHktcHJvdmlkZXIuZGV0YS5kZXYiLCJpYXQiOjE2Njc0MTc0NzcuMjAxMzM2LCJleHAiOjE2Njc0MTg2NzguMjAxMzYyfQ.nH-0oHY_74lV_TozZL2ftVxVJclVtolFA_3UsLQox0o"
    }
    #ACT
    response = client.delete("/users", json={"password":"testpassword1"}, headers=del_user)
    #ASSERT
    assert response.status_code == 204