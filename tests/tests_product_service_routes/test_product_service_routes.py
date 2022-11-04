from fastapi.testclient import TestClient
from decouple import config
from main import app

def test_post_products_endpoint_success():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN = config("VALID_TOKEN")
    test_product = {
        "ownerId":TEST_USER_ID,
        "name":"test new product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"new product from post request",
        "price":0.0
    }
    auth_header = {
          "token": VALID_TOKEN
    }
    #ACT
    response = client.post("/products",json=test_product, headers=auth_header)
    #ASSERT
    response_product = response.json()
    assert response.status_code == 201
    assert test_product.items() <=response_product.items()
    #CLEANUP
    client.delete(f"/products/{response_product['productId']}",headers=auth_header)

    

def test_post_products_endpoint_fails_invalid_token():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    test_product = {
        "ownerId":TEST_USER_ID,
        "name":"test new product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"new product from post request",
        "price":0.0
    }
    auth_header = {
          "token": "invalid token"
    }
    expected_error = {
        "detail": "Invalid token"
    }
    #ACT
    response = client.post("/products",json=test_product, headers=auth_header)
    #ASSERT
    assert response.status_code == 403
    assert response.json() == expected_error


def test_post_products_endpoint_fails_by_creating_not_owned_product():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN = config("VALID_TOKEN")
    test_product = {
        "ownerId":"different user id",
        "name":"test new product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"new product from post request",
        "price":0.0
    }
    auth_header = {
          "token": VALID_TOKEN
    }
    expected_error = {
        "detail": "Users are only allowed to create products for themselves."
    }
    #ACT
    response = client.post("/products",json=test_product, headers=auth_header)
    #ASSERT
    assert response.status_code == 403
    assert response.json() == expected_error


def test_get_products_endpoint_returns_products_for_user():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN = config("VALID_TOKEN")
    expected_product = {
        "productId":"29f6f518-53a8-11ed-a980-cd9f67f7363d",
        "ownerId":TEST_USER_ID,
        "name":"test product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"test product for get method",
        "price":0.0
    }
    auth_header = {
          "token": VALID_TOKEN
    }
    #ACT
    response = client.get(f"/products", headers=auth_header)
    #ASSERT
    assert response.status_code == 200
    assert expected_product in response.json()


def test_get_products_endpoint_fails_invalid_token():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    auth_header = {
          "token": "invalid_token"
    }
    expected_error = {
        "detail": "Invalid token"
    }
    #ACT
    get_response = client.get(f"/products", headers=auth_header)
    #ASSERT
    assert get_response.status_code == 403
    assert get_response.json() == expected_error


def test_get_single_product_endpoint_returns_product_for_user_by_id():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN = config("VALID_TOKEN")
    expected_product = {
        "productId":"29f6f518-53a8-11ed-a980-cd9f67f7363d",
        "ownerId":TEST_USER_ID,
        "name":"test product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"test product for get method",
        "price":0.0
    }
    expected_product_id = expected_product['productId']
    auth_header = {
          "token": VALID_TOKEN
    }
    #ACT
    response = client.get(f"/products/{expected_product_id}", headers=auth_header)
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
    auth_header = {
          "token": "invalid_token"
    }
    #ACT
    response = client.get("/products/not_existing_id", headers=auth_header)
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
    auth_header = {
          "token": VALID_TOKEN
    }
    #ACT
    response = client.get("/products/not_existing_id", headers=auth_header)
    #ASSERT
    assert response.status_code == 404
    assert response.json() == expected_error


def test_get_single_product_endpoint_fails_for_not_owned_product():
    #ARRANGE
    client = TestClient(app)
    VALID_TOKEN = config("VALID_TOKEN")
    expected_error = {
        "detail": "User is not allowed to get a product not owned."
    }
    auth_header = {
          "token": VALID_TOKEN
    }
    #ACT
    response = client.get("/products/12345", headers=auth_header)
    #ASSERT
    assert response.status_code == 403
    assert response.json() == expected_error


def test_patch_endpoint_updates_owned_product_success():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN = config("VALID_TOKEN")
    test_product = {
        "ownerId":TEST_USER_ID,
        "name":"test new product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"new product from post request",
        "price":0.0
    }
    updated_test_product = {
        "ownerId":TEST_USER_ID,
        "name":"test patched product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"updated product from patch request",
        "price":0.0
    }
    auth_header = {
          "token": VALID_TOKEN
    }
    post_response = client.post("/products",json=test_product, headers=auth_header)
    test_product_id = post_response.json()["productId"]
    #ACT
    patch_response = client.patch(f"/products/{test_product_id}",json=updated_test_product, headers=auth_header)
    #ASSERT
    assert patch_response.status_code == 204
    #CLEANUP
    client.delete(f"/products/{response_product_id}",headers=auth_header)


def test_patch_endpoint_fails_invalid_token():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN = config("VALID_TOKEN")
    updated_test_product = {
        "ownerId":TEST_USER_ID,
        "name":"test patched product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"updated product from patch request",
        "price":0.0
    }
    expected_error = {
        "detail": "Invalid token"
    }
    auth_header = {
          "token": "invalid_token"
    }
    #ACT
    patch_response = client.patch("/products/12345",json=updated_test_product, headers=auth_header)
    #ASSERT
    assert patch_response.status_code == 403
    assert patch_response.json() == expected_error

    
def test_patch_endpoint_fails_updating_not_owned_product():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN = config("VALID_TOKEN")
    updated_test_product = {
        "ownerId":TEST_USER_ID,
        "name":"test patched product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"updated product from patch request",
        "price":0.0
    }
    expected_error = {
        "detail": "Modifications are only allowed by the owner of the product."
    }
    auth_header = {
          "token": VALID_TOKEN
    }
    #ACT
    patch_response = client.patch("/products/12345",json=updated_test_product, headers=auth_header)
    #ASSERT
    assert patch_response.status_code == 403
    assert patch_response.json() == expected_error


def test_patch_endpoint_fails_updating_not_existing_product():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN = config("VALID_TOKEN")
    updated_test_product = {
        "ownerId":TEST_USER_ID,
        "name":"test patched product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"updated product from patch request",
        "price":0.0
    }
    expected_error = {
        "detail": "Product not found."
    }
    auth_header = {
          "token": VALID_TOKEN
    }
    #ACT
    patch_response = client.patch("/products/not_existing_id",json=updated_test_product, headers=auth_header)
    #ASSERT
    assert patch_response.status_code == 404
    assert patch_response.json() == expected_error
    
    


def test_delete_product_endpoint_success():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN = config("VALID_TOKEN")
    test_product = {
        "ownerId":TEST_USER_ID,
        "name":"test new product",
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "description":"new product from post request",
        "price":0.0
    }
    auth_header = {
          "token": VALID_TOKEN
    }
    post_response = client.post("/products",json=test_product, headers=auth_header)
    product_id = post_response.json()["productId"]
    #ACT
    del_response = client.delete(f"/products/{product_id}",headers=auth_header)
    #ASSERT
    assert del_response.status_code == 204


def test_delete_product_endpoint_fails_invalid_token():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    auth_header = {
          "token": "invalid_token"
    }
    expected_error = {
        "detail": "Invalid token"
    }
    #ACT
    del_response = client.delete("/products/some_product_id",headers=auth_header)
    #ASSERT
    assert del_response.status_code == 403
    assert del_response.json() == expected_error


def test_delete_product_endpoint_fails_for_not_owned_product():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    VALID_TOKEN = config("VALID_TOKEN")
    auth_header = {
          "token": VALID_TOKEN
    }
    expected_error = {
        "detail": "User is not allowed to delete a product not owned."
    }
    #ACT
    del_response = client.delete("/products/12345",headers=auth_header)
    #ASSERT
    assert del_response.status_code == 403
    assert del_response.json() == expected_error