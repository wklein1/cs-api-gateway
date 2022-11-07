from fastapi.testclient import TestClient
from decouple import config
from main import app
from routes.product_service_routes import router

def test_post_products_endpoint_success():
    #ARRANGE
    client = TestClient(app)

    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN = config("VALID_TOKEN")
    test_product = {
        "name":"test new product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"new product from post request",
    }
    expected_response_product = {
        "name":"test new product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"new product from post request",
        "price":638.9
    }
    auth_cookie = {
          "token": VALID_TOKEN
    }
    #ACT
    response = client.post("/products",json=test_product, cookies=auth_cookie)
    #ASSERT
    response_product = response.json()
    assert response.status_code == 201
    assert expected_response_product.items() <=response_product.items()
    #CLEANUP
    client.delete(f"/products/{response_product['id']}",cookies=auth_cookie)

    

def test_post_products_endpoint_fails_invalid_token():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    test_product = {
        "name":"test new product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"new product from post request",
    }
    auth_cookie = {
          "token": "invalid token"
    }
    expected_error = {
        "detail": "Invalid token"
    }
    #ACT
    response = client.post("/products",json=test_product, cookies=auth_cookie)
    #ASSERT
    assert response.status_code == 403
    assert response.json() == expected_error


def test_get_products_endpoint_returns_products_for_user():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN = config("VALID_TOKEN")
    expected_product = {
        "id":"29f6f518-53a8-11ed-a980-cd9f67f7363d",
        "name":"test product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"test product for get method",
        "price":638.9
    }
    auth_cookie = {
          "token": VALID_TOKEN
    }
    #ACT
    response = client.get(f"/products", cookies=auth_cookie)
    #ASSERT
    assert response.status_code == 200
    assert expected_product in response.json()


def test_get_products_endpoint_fails_invalid_token():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    auth_cookie = {
          "token": "invalid_token"
    }
    expected_error = {
        "detail": "Invalid token"
    }
    #ACT
    get_response = client.get(f"/products", cookies=auth_cookie)
    #ASSERT
    assert get_response.status_code == 403
    assert get_response.json() == expected_error


def test_get_single_product_endpoint_returns_product_for_user_by_id():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN = config("VALID_TOKEN")
    expected_product = {
        "id":"29f6f518-53a8-11ed-a980-cd9f67f7363d",
        "name":"test product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"test product for get method",
        "price":638.9
    }
    expected_product_id = expected_product['id']
    auth_cookie = {
          "token": VALID_TOKEN
    }
    #ACT
    response = client.get(f"/products/{expected_product_id}", cookies=auth_cookie)
    #ASSERT
    assert response.status_code == 200
    assert response.json() == expected_product

def test_get_single_product_endpoint_fails_invalid_token():
    #ARRANGE
    client = TestClient(app)
    VALID_TOKEN = config("VALID_TOKEN")
    expected_error = {
        "detail": "Invalid token"
    }
    auth_cookie = {
          "token": "invalid_token"
    }
    #ACT
    response = client.get("/products/not_existing_id", cookies=auth_cookie)
    #ASSERT
    assert response.status_code == 403
    assert response.json() == expected_error

def test_get_single_product_endpoint_fails_for_not_existing_product():
    #ARRANGE
    client = TestClient(app)
    VALID_TOKEN = config("VALID_TOKEN")
    expected_error = {
        "detail": "Product not found."
    }
    auth_cookie = {
          "token": VALID_TOKEN
    }
    #ACT
    response = client.get("/products/not_existing_id", cookies=auth_cookie)
    #ASSERT
    assert response.status_code == 404
    assert response.json() == expected_error


def test_patch_endpoint_updates_product_success():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN = config("VALID_TOKEN")
    test_product = {
        "name":"test new product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"new product from post request",
        
    }
    updated_test_product = {
        "name":"test patched product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"updated product from patch request",
    }
    auth_cookie = {
          "token": VALID_TOKEN
    }
    post_response = client.post("/products",json=test_product, cookies=auth_cookie)
    test_product_id = post_response.json()["id"]
    #ACT
    patch_response = client.patch(f"/products/{test_product_id}",json=updated_test_product, cookies=auth_cookie)
    #ASSERT
    assert patch_response.status_code == 204
    #CLEANUP
    client.delete(f"/products/{test_product_id}",cookies=auth_cookie)


def test_patch_endpoint_fails_invalid_token():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN = config("VALID_TOKEN")
    updated_test_product = {
        "name":"test patched product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"updated product from patch request",
    }
    expected_error = {
        "detail": "Invalid token"
    }
    auth_cookie = {
          "token": "invalid_token"
    }
    #ACT
    patch_response = client.patch("/products/12345",json=updated_test_product, cookies=auth_cookie)
    #ASSERT
    assert patch_response.status_code == 403
    assert patch_response.json() == expected_error


def test_patch_endpoint_fails_updating_not_existing_product():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN = config("VALID_TOKEN")
    updated_test_product = {
        "name":"test patched product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"updated product from patch request",
    }
    expected_error = {
        "detail": "Product not found."
    }
    auth_cookie = {
          "token": VALID_TOKEN
    }
    #ACT
    patch_response = client.patch("/products/not_existing_id",json=updated_test_product, cookies=auth_cookie)
    #ASSERT
    assert patch_response.status_code == 404
    assert patch_response.json() == expected_error
    

def test_delete_product_endpoint_success():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN = config("VALID_TOKEN")
    test_product = {
        "name":"test new product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"new product from post request",
    }
    auth_cookie = {
          "token": VALID_TOKEN
    }
    post_response = client.post("/products",json=test_product, cookies=auth_cookie)
    product_id = post_response.json()["id"]
    #ACT
    del_response = client.delete(f"/products/{product_id}",cookies=auth_cookie)
    #ASSERT
    assert del_response.status_code == 204


def test_delete_product_endpoint_fails_invalid_token():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    auth_cookie = {
          "token": "invalid_token"
    }
    expected_error = {
        "detail": "Invalid token"
    }
    #ACT
    del_response = client.delete("/products/some_product_id",cookies=auth_cookie)
    #ASSERT
    assert del_response.status_code == 403
    assert del_response.json() == expected_error