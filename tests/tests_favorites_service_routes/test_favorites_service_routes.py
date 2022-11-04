from fastapi.testclient import TestClient
from decouple import config
from main import app


def test_post_favorite_endpoint_adds_component_favorite_to_list():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN = config("VALID_TOKEN")
    expected_favorites_obj = {
        "ownerId":TEST_USER_ID,
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d","546c08de-539d-11ed-a980-cd9f67f7363d"],
        "productIds":[]
    }
    auth_header = {
          "token": VALID_TOKEN
    }
    #ACT
    response = client.post("/favorites/items",json={"id":"546c08de-539d-11ed-a980-cd9f67f7363d","itemType":"component"}, headers=auth_header)
    #ASSERT
    assert response.status_code == 204
    #CLEANUP
    client.delete("/favorites/items",json={"id":"546c08de-539d-11ed-a980-cd9f67f7363d","itemType":"component"}, headers=auth_header)

    

def test_post_favorite_endpoint_fails_invalid_token():
    #ARRANGE
    client = TestClient(app)
    expected_error = {
        "detail": "Invalid token"
    }
    auth_header = {
          "token": "invalid_token"
    }
    #ACT
    response = client.post("/favorites/items",json={"id":"546c08d7-539d-11ed-a980-cd9f67f7363d","itemType":"component"}, headers=auth_header)
    #ASSERT
    assert response.status_code == 403
    assert response.json() == expected_error


def test_post_favorite_endpoint_fails_to_add_already_added_product_to_favorites():
    #ARRANGE
    client = TestClient(app)
    VALID_TOKEN = config("VALID_TOKEN")
    expected_error = {
        "detail": "Item is already in favorites list."
    }
    auth_header = {
          "token": VALID_TOKEN
    }
    client.post("/favorites/items",json={"id":"29f6f518-53a8-11ed-a980-cd9f67f7363d","itemType":"product"}, headers=auth_header)
    #ACT
    response = client.post("/favorites/items",json={"id":"29f6f518-53a8-11ed-a980-cd9f67f7363d","itemType":"product"}, headers=auth_header)
    #ASSERT
    assert response.status_code == 409
    assert response.json() == expected_error


def test_post_favorite_endpoint_fails_to_add_already_added_component_to_favorites():
    #ARRANGE
    client = TestClient(app)
    VALID_TOKEN = config("VALID_TOKEN")
    expected_error = {
        "detail": "Item is already in favorites list."
    }
    auth_header = {
          "token": VALID_TOKEN
    }
    #ACT
    response = client.post("/favorites/items",json={"id":"546c08d7-539d-11ed-a980-cd9f67f7363d","itemType":"component"}, headers=auth_header)
    #ASSERT
    assert response.status_code == 409
    assert response.json() == expected_error


def test_delete_favorite_endpoint_fails_invalid_token():
    #ARRANGE
    client = TestClient(app)
    expected_error = {
        "detail": "Invalid token"
    }
    auth_header = {
          "token": "invalid_token"
    }
    #ACT
    delete_favorite_response = client.delete("/favorites/items",json={"id":"29f6f518-53a8-11ed-a980-cd9f67f7363d","itemType":"product"}, headers=auth_header)
    #ASSERT
    assert delete_favorite_response.status_code == 403
    assert delete_favorite_response.json() == expected_error


def test_delete_favorite_endpoint_deletes_product_favorite_success():
    #ARRANGE
    client = TestClient(app)
    VALID_TOKEN = config("VALID_TOKEN")
    auth_header = {
          "token": VALID_TOKEN
    }
    client.post("/favorites/items",json={"id":"29f6f518-53a8-11ed-a980-cd9f67f7363d","itemType":"product"},headers=auth_header)
    #ACT
    response = client.delete("/favorites/items",json={"id":"29f6f518-53a8-11ed-a980-cd9f67f7363d","itemType":"product"}, headers=auth_header)
    #ASSERT
    assert response.status_code == 204


def test_delete_favorite_endpoint_deletes_component_favorite_success():
    #ARRANGE
    client = TestClient(app)
    VALID_TOKEN = config("VALID_TOKEN")
    auth_header = {
          "token": VALID_TOKEN
    }
    client.post("/favorites/items",json={"id":"546c08de-539d-11ed-a980-cd9f67f7363d","itemType":"component"},headers=auth_header)
    #ACT
    response = client.delete("/favorites/items",json={"id":"546c08de-539d-11ed-a980-cd9f67f7363d","itemType":"component"}, headers=auth_header)
    #ASSERT
    assert response.status_code == 204