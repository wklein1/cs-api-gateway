from fastapi import FastAPI, APIRouter, HTTPException, status, Cookie
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime,timedelta
from decouple import config
import requests
from models.component_model import Component
from models import error_models, currency_models, auth_models, user_models, product_models, favorites_models
from modules.jwt.jwt_module import JwtEncoder
from utils import decode_auth_token

JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITHM="HS256"
IDENTITY_PROVIDER_ACCESS_KEY = config("IDENTITY_PROVIDER_ACCESS_KEY")

identity_provider_jwt_encoder = JwtEncoder(secret=IDENTITY_PROVIDER_ACCESS_KEY, algorithm=JWT_ALGORITHM)

router = APIRouter(
    prefix="/users",
    tags=["user data (identity provider)"]
)

@router.get(
    "/{user_id}",
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
)
async def get_user_data(user_id:str, token: str = Cookie()):
    
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


@router.patch(
    "/{user_id}",
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
)
async def patch_user_by_id(user_data: user_models.UserUpdatesInModel, user_id: str, token: str = Cookie()):
    
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


@router.patch(
    "/{user_id}/password",
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
)
async def change_user_password_by_id(change_password_data: user_models.UserChangePasswordInModel, user_id: str, token: str = Cookie()):
    
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
       

@router.delete(
     "",
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
)
async def delete_user(passwordIn:auth_models.PasswordInModel, token: str = Cookie()):
    
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
