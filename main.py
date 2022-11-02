from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from models.component_model import Component
from models import error_models, currency_models
from decouple import config
import requests

COMPONENTS_SERVICE_API_KEY = config("COMPONENTS_SERVICE_API_KEY")

app = FastAPI()

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
    headers = {'Content-Type': 'application/json','X-API-Key':COMPONENTS_SERVICE_API_KEY}
    response = requests.get("https://cs-currency-service.deta.dev/currencies", headers=headers)
    if response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    if response.json() == {}:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return response.json()