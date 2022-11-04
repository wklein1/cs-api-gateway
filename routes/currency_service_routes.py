from fastapi import FastAPI, APIRouter, HTTPException, status,Header
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
CURRENCY_SERVICE_ACCESS_KEY = config("CURRENCY_SERVICE_ACCESS_KEY")

currency_service_jwt_encoder = JwtEncoder(secret=CURRENCY_SERVICE_ACCESS_KEY, algorithm=JWT_ALGORITHM)

router = APIRouter(
    prefix="/currencies",
    tags=["currency microservice"]
)

@router.get(
    "",
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


@router.get(
    "/{old_currency_code}/{new_currency_code}",
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

