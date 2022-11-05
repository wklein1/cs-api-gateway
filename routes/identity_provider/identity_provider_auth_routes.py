from fastapi import FastAPI, APIRouter, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime,timedelta
from decouple import config
import requests
from models.component_model import Component
from models import error_models, auth_models, user_models
from modules.jwt.jwt_module import JwtEncoder
from utils import decode_auth_token

JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITHM="HS256"
IDENTITY_PROVIDER_ACCESS_KEY = config("IDENTITY_PROVIDER_ACCESS_KEY")

identity_provider_jwt_encoder = JwtEncoder(secret=IDENTITY_PROVIDER_ACCESS_KEY, algorithm=JWT_ALGORITHM)

router = APIRouter(
    tags=["auth (identity provider)"]
)

@router.post(
    "/register",
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
    response_description="Returns an object with the user name of the registered user'.",
)
async def register_user(user_data: user_models.UserInModel, response : Response):
    
    identity_provider_access_token = identity_provider_jwt_encoder.generate_jwt({"exp":(datetime.now() + timedelta(minutes=1)).timestamp()})
    
    headers = {'Content-Type': 'application/json', 'microserviceAccessToken':identity_provider_access_token}
    post_user_response = requests.post(f"https://cs-identity-provider.deta.dev/users", json=user_data.dict(), headers=headers)
    
    if post_user_response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Request to microservice failed")
    
    if post_user_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=post_user_response.json())

    token = post_user_response.json()["token"]
    response.set_cookie(key="token",value=token, httponly=True) 
    return post_user_response.json()


@router.post(
    "/login",
    description="Authenticate a user.",
    response_model=auth_models.AuthResponseModel,
    response_description="Returns an object with the user name and access token for the authenticated user'.",
    responses={ 
        403 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if provided credentials are invalid"
        }},
)
async def login_user(user_data: auth_models.LoginModel, response : Response):
    
    identity_provider_access_token = identity_provider_jwt_encoder.generate_jwt({"exp":(datetime.now() + timedelta(minutes=1)).timestamp()})
    
    headers = {'Content-Type': 'application/json', 'microserviceAccessToken':identity_provider_access_token}
    login_user_response = requests.post(f"https://cs-identity-provider.deta.dev/login", json=user_data.dict(), headers=headers)

    if login_user_response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Request to microservice failed")
    
    if login_user_response.status_code == status.HTTP_403_FORBIDDEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    token = login_user_response.json()["token"]
    response.set_cookie(key="token",value=token, httponly=True) 

    return login_user_response.json()