from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import requests
from models.component_model import Component

router = APIRouter(
    prefix="/components",
    tags=["components microservice"]
)

@router.get(
    "",
    response_model=list[Component],
    response_description="Returns list of components.",
    description="Get all available components.", 
)
async def get_components():
    headers = {'Content-Type': 'application/json'}
    response = requests.get("https://cs-components-service.deta.dev/components", headers=headers)
    return response.json()
