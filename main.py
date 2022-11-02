from fastapi import FastAPI, HTTPException, status,Header
from fastapi.middleware.cors import CORSMiddleware
from models.component_model import Component
from models import error_models, currency_models, auth_models, user_models
from modules.jwt.jwt_module import JwtEncoder
from datetime import datetime,timedelta
from decouple import config
import requests

COMPONENTS_SERVICE_API_KEY = config("COMPONENTS_SERVICE_API_KEY")
IDENTITY_PROVIDER_ACCESS_KEY = config("IDENTITY_PROVIDER_ACCESS_KEY")
JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITHM="HS256"
JWT_AUDIENCE="kbe-aw2022-frontend.netlify.app"
JWT_ISSUER="cs-identity-provider.deta.dev"

app = FastAPI()

jwt_encoder = JwtEncoder(secret=JWT_SECRET, algorithm=JWT_ALGORITHM)
identity_provider_jwt_encoder = JwtEncoder(secret=IDENTITY_PROVIDER_ACCESS_KEY, algorithm=JWT_ALGORITHM)

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

def decode_auth_token(token:str)->dict:
    try:
        return jwt_encoder.decode_jwt(token=token,audience=JWT_AUDIENCE,issuer=JWT_ISSUER)
    except:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

@app.get(
    "/components",
    response_model=list[Component],
    response_description="Returns list of components.",
    description="Get all available components.", 
)
async def get_components():
    headers = {'Content-Type': 'application/json','X-API-Key':COMPONENTS_SERVICE_API_KEY}
    response = requests.get("https://cs-components-service.deta.dev/components", headers=headers)
    return response.json()


@app.get(
    "/currencies",
    response_model=list[currency_models.CurrencyModel],
    response_description="Returns list of available currencies",
    responses={503 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if microservice request fails."
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
        },
        409 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if the provided username is already taken."
        }},
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
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    if post_user_response.status_code == status.HTTP_409_CONFLICT:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User name is already taken")

    return post_user_response.json()

@app.post(
    "/login",
    description="Authenticate a user.",
    response_model=auth_models.AuthResponseModel,
    response_description="Returns an object with the user name and access token for the authenticated user'.",
    tags=["auth (identity provider)"]
)
async def login_user(user_data: auth_models.LoginModel):
    
    identity_provider_access_token = identity_provider_jwt_encoder.generate_jwt({"exp":(datetime.now() + timedelta(minutes=1)).timestamp()})
    
    headers = {'Content-Type': 'application/json', 'microserviceAccessToken':identity_provider_access_token}
    login_user_response = requests.post(f"https://cs-identity-provider.deta.dev/login", json=user_data.dict(), headers=headers)

    if login_user_response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Request to microservice failed")
    
    if login_user_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    return login_user_response.json()



@app.delete(
     "/users",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={503 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if microservice request fails."
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
