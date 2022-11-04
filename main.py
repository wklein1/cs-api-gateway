from fastapi import FastAPI, HTTPException, status,Header
from fastapi.middleware.cors import CORSMiddleware
from models.component_model import Component
from models import error_models, currency_models, auth_models, user_models, product_models, favorites_models
from modules.jwt.jwt_module import JwtEncoder
from datetime import datetime,timedelta
from decouple import config
import requests

IDENTITY_PROVIDER_ACCESS_KEY = config("IDENTITY_PROVIDER_ACCESS_KEY")
PRODUCT_SERVICE_ACCESS_KEY = config("PRODUCT_SERVICE_ACCESS_KEY")
FAVORITES_SERVICE_ACCESS_KEY = config("FAVORITES_SERVICE_ACCESS_KEY")
JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITHM="HS256"
JWT_AUDIENCE="kbe-aw2022-frontend.netlify.app"
JWT_ISSUER="cs-identity-provider.deta.dev"

app = FastAPI()

jwt_encoder = JwtEncoder(secret=JWT_SECRET, algorithm=JWT_ALGORITHM)
identity_provider_jwt_encoder = JwtEncoder(secret=IDENTITY_PROVIDER_ACCESS_KEY, algorithm=JWT_ALGORITHM)
product_service_jwt_encoder = JwtEncoder(secret=PRODUCT_SERVICE_ACCESS_KEY, algorithm=JWT_ALGORITHM)
favorites_service_jwt_encoder = JwtEncoder(secret=FAVORITES_SERVICE_ACCESS_KEY, algorithm=JWT_ALGORITHM)

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"])

def decode_auth_token(token:str)->dict|None:
    try:
        return jwt_encoder.decode_jwt(token=token,audience=JWT_AUDIENCE,issuer=JWT_ISSUER)
    except:
        return None

@app.get(
    "/components",
    response_model=list[Component],
    response_description="Returns list of components.",
    description="Get all available components.", 
)
async def get_components():
    headers = {'Content-Type': 'application/json'}
    response = requests.get("https://cs-components-service.deta.dev/components", headers=headers)
    return response.json()


@app.get(
    "/currencies",
    response_model=list[currency_models.CurrencyModel],
    response_description="Returns list of available currencies",
    responses={503 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if request to microservice fails."
        }},
    description="Get all available currencies.",   
    tags=["currency microservice"] 
)
async def get_currencies():
    headers = {'Content-Type': 'application/json'}
    response = requests.get("https://cs-currency-service.deta.dev/currencies", headers=headers)
    if response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    if response.json() == {}:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return response.json()


@app.get(
    "/currencies/{old_currency_code}/{new_currency_code}",
    response_model=currency_models.ExchangeRateResponseModel,
    response_description="Returns exchange rate from old currency to new",
    responses={503 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if microservice request fails."
        }},
    description="Get exchange rate from old currency to new.",
    tags=["currency microservice"] 
)
async def get_currency_exchange_rate(old_currency_code, new_currency_code):
    headers = {'Content-Type': 'application/json'}
    response = requests.get(f"https://cs-currency-service.deta.dev/currencies/{old_currency_code}/{new_currency_code}", headers=headers)
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return response.json()


@app.post(
    "/users",
    description="Register a new user.",
    status_code=status.HTTP_201_CREATED,
    responses={ 
        503 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if microservice request fails."
        },
        422 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if provided user data is not valid."
        },},
    response_model=auth_models.AuthResponseModel,
    response_description="Returns an object with the user name and access token for the registered user'.",
    tags=["auth (identity provider)"]
)
async def register_user(user_data: user_models.UserInModel):
    
    identity_provider_access_token = identity_provider_jwt_encoder.generate_jwt({"exp":(datetime.now() + timedelta(minutes=1)).timestamp()})
    
    headers = {'Content-Type': 'application/json', 'microserviceAccessToken':identity_provider_access_token}
    post_user_response = requests.post(f"https://cs-identity-provider.deta.dev/users", json=user_data.dict(), headers=headers)
    
    if post_user_response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Request to microservice failed")
    
    if post_user_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=post_user_response.json())

    return post_user_response.json()


@app.post(
    "/login",
    description="Authenticate a user.",
    response_model=auth_models.AuthResponseModel,
    response_description="Returns an object with the user name and access token for the authenticated user'.",
    responses={ 
        403 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if provided credentials are invalid"
        }},
    tags=["auth (identity provider)"]
)
async def login_user(user_data: auth_models.LoginModel):
    
    identity_provider_access_token = identity_provider_jwt_encoder.generate_jwt({"exp":(datetime.now() + timedelta(minutes=1)).timestamp()})
    
    headers = {'Content-Type': 'application/json', 'microserviceAccessToken':identity_provider_access_token}
    login_user_response = requests.post(f"https://cs-identity-provider.deta.dev/login", json=user_data.dict(), headers=headers)

    if login_user_response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Request to microservice failed")
    
    if login_user_response.status_code == status.HTTP_403_FORBIDDEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    return login_user_response.json()


@app.get(
    "/users/{user_id}",
    description="Get user data of a given user.",
    responses={ 
        404 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if the user could not be found."
        },
        403 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if the provided token is invalid."
        },
        401 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if request is unauthorized."
        }},
    response_model=user_models.UserOutModel,
    response_description="Returns an object with user data.",
    tags=["user data (identity provider)"]
)
async def get_user_data(user_id:str, token: str = Header()):
    
    decoded_token = decode_auth_token(token)
    if decoded_token is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    token_user_id = decoded_token["userId"]
    if token_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized to get this data")

    identity_provider_access_token = identity_provider_jwt_encoder.generate_jwt({"exp":(datetime.now() + timedelta(minutes=1)).timestamp()})
    
    headers = {'Content-Type': 'application/json', 'userId':user_id, 'microserviceAccessToken':identity_provider_access_token}
    get_user_data_response = requests.get(f"https://cs-identity-provider.deta.dev/users/{user_id}", headers=headers)
    
    if get_user_data_response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return get_user_data_response.json()


@app.patch(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Returns no data.",
    responses={
        503 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if request to microservice fails."
        },
        422 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if provided user updates are not valid."
        },
        403 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if provided password or token is invalid."
            },
        401 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if request is unauthorized."
        },
        404 :{
                "model": error_models.HTTPErrorModel,
                "description": "Error raised if the user can not be found."
        }},
    description="Updates user with values specified in request body.",
    tags=["user data (identity provider)"]
)
async def patch_user_by_id(user_data: user_models.UserUpdatesInModel, user_id: str, token: str = Header()):
    
    decoded_token = decode_auth_token(token)
    if decoded_token is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    token_user_id = decoded_token["userId"]
    if token_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized to change this data")
    
    identity_provider_access_token = identity_provider_jwt_encoder.generate_jwt({"exp":(datetime.now() + timedelta(minutes=1)).timestamp()})
    
    headers = {'Content-Type': 'application/json', 'userId':user_id, 'microserviceAccessToken':identity_provider_access_token}
    patch_data_response = requests.patch(f"https://cs-identity-provider.deta.dev/users/{user_id}", json=user_data.dict(), headers=headers)
    
    if patch_data_response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
   
    if patch_data_response.status_code == status.HTTP_403_FORBIDDEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid password")
    
    if patch_data_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=patch_data_response.json())

    if patch_data_response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Request to microservice failed")
    # All checks passed:
    return


@app.patch(
    "/users/{user_id}/password",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Returns no data.",
    responses={
        503 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if database request fails."
        },
        422 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if password update is not valid."
        },
        401 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if request is unauthorized."
        },
        403 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if user password is invalid."
            },
        404 :{
                "model": error_models.HTTPErrorModel,
                "description": "Error raised if the user can not be found."
        }},
    description="Updates the user password.",
    tags=["user data"]
)
async def change_user_password_by_id(change_password_data: user_models.UserChangePasswordInModel, user_id: str, token: str = Header()):
    
    user_change_password_dict = change_password_data.dict()
    new_password = user_change_password_dict["new_password"]

    decoded_token = decode_auth_token(token)
    if decoded_token is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    token_user_id = decoded_token["userId"]
    if token_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized to change this data")
    
    identity_provider_access_token = identity_provider_jwt_encoder.generate_jwt({"exp":(datetime.now() + timedelta(minutes=1)).timestamp()})
    
    headers = {'Content-Type': 'application/json', 'userId':user_id, 'microserviceAccessToken':identity_provider_access_token}
    patch_password_response = requests.patch(f"https://cs-identity-provider.deta.dev/users/{user_id}/password", json=change_password_data.dict(), headers=headers)

    if patch_password_response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Request to microservice failed")
    
    if patch_password_response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
   
    if patch_password_response.status_code == status.HTTP_403_FORBIDDEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid password")
    
    if patch_password_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=patch_password_response.json())
    # All checks passed:
    return
       

@app.delete(
     "/users",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={503 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if request to microservice fails."
        },
        403 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if the provided password is invalid."
        }},
    description="Deletes a user.",
    tags=["user data (identity provider)"]

)
async def delete_user(passwordIn:auth_models.PasswordInModel, token: str = Header()):
    
    decoded_token = decode_auth_token(token)
    if decoded_token is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    user_id = decoded_token["userId"]
    identity_provider_access_token = identity_provider_jwt_encoder.generate_jwt({"exp":(datetime.now() + timedelta(minutes=1)).timestamp()})
    
    headers = {'Content-Type': 'application/json', 'userId':user_id, 'microserviceAccessToken':identity_provider_access_token}
    delete_user_response = requests.delete(f"https://cs-identity-provider.deta.dev/users", json=passwordIn.dict(), headers=headers)
    
    if delete_user_response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Request to microservice failed")
    
    if delete_user_response.status_code == status.HTTP_403_FORBIDDEN:
        if delete_user_response.json() == {"detail":"Invalid token"}:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Request to microservice failed")
        elif {"detail":"Invalid password"}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid password")

@app.get(
    "/products",
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


@app.get(
    "/products/{product_id}", 
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
    

@app.post(
    "/products",
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
    
    headers = {'Content-Type': 'application/json', 'userId':user_id, 'microserviceAccessToken':product_service_access_token}
    post_product_response = requests.post(f"https://cs-product-service.deta.dev/products", json=product.dict(), headers=headers)
    
    if post_product_response.status_code == status.HTTP_403_FORBIDDEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Users are only allowed to create products for themselves.")

    if post_product_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=post_product_response.json())

    return post_product_response.json()


@app.patch(
    "/products/{product_id}",
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
    
    headers = {'Content-Type': 'application/json', 'userId':user_id, 'microserviceAccessToken':product_service_access_token}
    patch_product_response = requests.patch(f"https://cs-product-service.deta.dev/products/{product_id}", json=product.dict(), headers=headers)
    
    if patch_product_response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    if patch_product_response.status_code == status.HTTP_403_FORBIDDEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Modifications are only allowed by the owner of the product.")

    if patch_product_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=patch_product_response.json())
    #all checks passed:
    return
        

@app.delete(
    "/products/{product_id}",
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
    
    headers = {'Content-Type': 'application/json', 'userId':user_id, 'microserviceAccessToken':product_service_access_token}
    delete_product_response = requests.delete(f"https://cs-product-service.deta.dev/products/{product_id}", headers=headers)
    
    if delete_product_response.status_code == status.HTTP_403_FORBIDDEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not allowed to delete a product not owned.")


@app.get(
    "/favorites",
    response_model=favorites_models.FavoritesModel,
    response_description="Returns favorites object with lists of product and component favorites",
    responses={403 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if provided token is invalid."
        },
        503 :{
            "model": error_models.HTTPErrorModel,
        }},
    description="Get all favorites belonging to a user.",    
)
async def get_favorites_for_user(token: str = Header()):
    decoded_token = decode_auth_token(token)
    if decoded_token is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    user_id = decoded_token["userId"]
    favorites_service_access_token = favorites_service_jwt_encoder.generate_jwt({"exp":(datetime.now() + timedelta(minutes=1)).timestamp()})
    
    headers = {'Content-Type': 'application/json', 'userId':user_id, 'microserviceAccessToken':favorites_service_access_token}
    get_favorites_response = requests.get("https://cs-favorites-service.deta.dev/favorites", headers=headers)

    if get_favorites_response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Request to microservice failed")
    
    return get_favorites_response.json()
   


@app.post(
    "/favorites/items",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={403 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if provided token is invalid."
        },
        409 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if item is already in favorites list."
        },
        503 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if microservice request fails."
        }},
    description="Adds an item to the favorites list of the user.",
)
async def adds_item_to_user_favorites_list(item_to_add:favorites_models.ToggleFavoriteModel, token: str = Header()):
   
    decoded_token = decode_auth_token(token)
    if decoded_token is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    user_id = decoded_token["userId"]
    favorites_service_access_token = favorites_service_jwt_encoder.generate_jwt({"exp":(datetime.now() + timedelta(minutes=1)).timestamp()})
    
    headers = {'Content-Type': 'application/json', 'userId':user_id, 'microserviceAccessToken':favorites_service_access_token}
    post_favorite_response = requests.post("https://cs-favorites-service.deta.dev/favorites/items", json=item_to_add.dict(), headers=headers)
   
    if post_favorite_response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Request to microservice failed")
   
    if post_favorite_response.status_code == status.HTTP_409_CONFLICT:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item is already in favorites list.")
    # all checks passed:
    return


@app.delete(    
     "/favorites/items",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={403 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if provided token is invalid."
        },
        503 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if database request fails."
        },
        422 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if provided item to delete is not valid."
        }},
    description="Removes an item from the favorites list of a user"
)
async def delete_item_from_favorites_for_user(item_to_remove:favorites_models.ToggleFavoriteModel, token: str = Header()):
    
    decoded_token = decode_auth_token(token)
    if decoded_token is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    user_id = decoded_token["userId"]
    favorites_service_access_token = favorites_service_jwt_encoder.generate_jwt({"exp":(datetime.now() + timedelta(minutes=1)).timestamp()})
    
    headers = {'Content-Type': 'application/json', 'userId':user_id, 'microserviceAccessToken':favorites_service_access_token}
    delete_favorite_response = requests.delete("https://cs-favorites-service.deta.dev/favorites/items", json=item_to_remove.dict(), headers=headers)
   
    if delete_favorite_response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Request to microservice failed")

    if delete_favorite_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=delete_favorite_response.json())
    # all checks passed:
    return