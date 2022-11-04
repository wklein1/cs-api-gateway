from fastapi import FastAPI, APIRouter, HTTPException, status,Header
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime,timedelta
from decouple import config
import requests
from models.component_model import Component
from models import error_models, product_models
from modules.jwt.jwt_module import JwtEncoder
from utils import decode_auth_token

JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITHM="HS256"
PRODUCT_SERVICE_ACCESS_KEY = config("PRODUCT_SERVICE_ACCESS_KEY")

product_service_jwt_encoder = JwtEncoder(secret=PRODUCT_SERVICE_ACCESS_KEY, algorithm=JWT_ALGORITHM)

router = APIRouter(
    prefix="/products",
    tags=["products microservice"]
)

@router.get(
    "",
    response_model=list[product_models.ProductResponseModel],
    response_description="Returns list with products",
    responses={403 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if the provided token is invalid."
        }},
    description="Get all products belonging to a user.",    
)
async def get_products_for_user(token: str = Header()):
    decoded_token = decode_auth_token(token)
    if decoded_token is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    user_id = decoded_token["userId"]
    product_service_access_token = product_service_jwt_encoder.generate_jwt({"exp":(datetime.now() + timedelta(minutes=1)).timestamp()})
    
    headers = {'Content-Type': 'application/json', 'userId':user_id, 'microserviceAccessToken':product_service_access_token}
    get_products_response = requests.get(f"https://cs-product-service.deta.dev/products", headers=headers)

    return get_products_response.json()


@router.get(
    "/{product_id}", 
    response_model=product_models.ProductResponseModel,
    response_description="Returns product",
    responses={
        403 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if the provided token is invalid or the user tries to get a product owned by a different user."
            },
        404 :{
                "model": error_models.HTTPErrorModel,
                "description": "Error raised if the product cant be found."
        }},
    description="Get a product by its id, belonging to the user."
)
async def get_product_by_id(product_id, token: str = Header()):
    decoded_token = decode_auth_token(token)
    if decoded_token is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    user_id = decoded_token["userId"]
    product_service_access_token = product_service_jwt_encoder.generate_jwt({"exp":(datetime.now() + timedelta(minutes=1)).timestamp()})
    
    headers = {'Content-Type': 'application/json', 'userId':user_id, 'microserviceAccessToken':product_service_access_token}
    get_product_response = requests.get(f"https://cs-product-service.deta.dev/products/{product_id}", headers=headers)

    if get_product_response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    if get_product_response.status_code == status.HTTP_403_FORBIDDEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not allowed to get a product not owned.")

    return get_product_response.json()
    

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=product_models.ProductResponseModel,
    response_description="Returns created product with generated id.",
    responses={403 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if the provided token is invalid or user tries to create a product for a different owner."
        },
        422 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if provided product data is not valid."
        }},
    description="Create a new product for a user",
)
async def post_product_by_user(product: product_models.ProductModel, token: str = Header()):
    decoded_token = decode_auth_token(token)
    if decoded_token is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    user_id = decoded_token["userId"]
    product_service_access_token = product_service_jwt_encoder.generate_jwt({"exp":(datetime.now() + timedelta(minutes=1)).timestamp()})
    
    headers = {'Content-Type':'application/json', 'userId':user_id, 'microserviceAccessToken':product_service_access_token}
    post_product_response = requests.post(f"https://cs-product-service.deta.dev/products", json=product.dict(), headers=headers)
    
    if post_product_response.status_code == status.HTTP_403_FORBIDDEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Users are only allowed to create products for themselves.")

    if post_product_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=post_product_response.json())

    return post_product_response.json()


@router.patch(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Returns no data.",
    responses={
        403 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if provided token is invalid or user tries to update a product not owned."
            },
        404 :{
                "model": error_models.HTTPErrorModel,
                "description": "Error raised if the product to update can not be found."
        },
        422 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if provided product updates are not valid."
        }},
    description="Updates product with values specified in request body.",
)
async def patch_product_by_id(product: product_models.ProductModel, product_id, token: str = Header()):
   
    decoded_token = decode_auth_token(token)
    if decoded_token is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    user_id = decoded_token["userId"]
    product_service_access_token = product_service_jwt_encoder.generate_jwt({"exp":(datetime.now() + timedelta(minutes=1)).timestamp()})
    
    headers = {'Content-Type':'application/json', 'userId':user_id, 'microserviceAccessToken':product_service_access_token}
    patch_product_response = requests.patch(f"https://cs-product-service.deta.dev/products/{product_id}", json=product.dict(), headers=headers)
    
    if patch_product_response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    if patch_product_response.status_code == status.HTTP_403_FORBIDDEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Modifications are only allowed by the owner of the product.")

    if patch_product_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=patch_product_response.json())
    #all checks passed:
    return
        

@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={403 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if provided token is invalid or user tries to delete a product not owned."
        }},
    description="Deletes a product by its id, if the user is the owner of the product.",
)
async def delete_product_by_id(product_id, token: str = Header()):
    decoded_token = decode_auth_token(token)
    if decoded_token is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    user_id = decoded_token["userId"]
    product_service_access_token = product_service_jwt_encoder.generate_jwt({"exp":(datetime.now() + timedelta(minutes=1)).timestamp()})
    
    headers = {'Content-Type':'application/json', 'userId':user_id, 'microserviceAccessToken':product_service_access_token}
    delete_product_response = requests.delete(f"https://cs-product-service.deta.dev/products/{product_id}", headers=headers)
    
    if delete_product_response.status_code == status.HTTP_403_FORBIDDEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not allowed to delete a product not owned.")
