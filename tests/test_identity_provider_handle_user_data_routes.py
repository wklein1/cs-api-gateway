from fastapi.testclient import TestClient
from fastapi import status
from decouple import config
from modules.jwt.jwt_module import JwtEncoder
from main import app

def test_delete_user_endpoint_invalid_password():
    #ARRANGE
    client = TestClient(app)
    del_user = {
          "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI4NWNiMzM5Zi01YWNiLTExZWQtYjdkYS02Mzk0M2E2ZTA2MTciLCJhdWQiOiJrYmUtYXcyMDIyLWZyb250ZW5kLm5ldGxpZnkuYXBwIiwiaXNzIjoiY3MtaWRlbnRpdHktcHJvdmlkZXIuZGV0YS5kZXYiLCJpYXQiOjE2Njc0MDY1NjguODczMjU4LCJleHAiOjE2Njc0MDc3NjkuODczMjc0fQ.IxZcCfurOncZdNfdZQOQGQq1L1rtRJzZGMvvAaRm-As"
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
          "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI4NWNiMzM5Zi01YWNiLTExZWQtYjdkYS02Mzk0M2E2ZTA2MTciLCJhdWQiOiJrYmUtYXcyMDIyLWZyb250ZW5kLm5ldGxpZnkuYXBwIiwiaXNzIjoiY3MtaWRlbnRpdHktcHJvdmlkZXIuZGV0YS5kZXYiLCJpYXQiOjE2Njc0MDY1NjguODczMjU4LCJleHAiOjE2Njc0MDc3NjkuODczMjc0fQ.IxZcCfurOncZdNfdZQOQGQq1L1rtRJzZGMvvAaRm-As"
    }
    #ACT
    response = client.delete("/users", json={"password":"testpassword1"}, headers=del_user)
    #ASSERT
    assert response.status_code == 204