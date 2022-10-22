from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.component_model import Component
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

@app.get("/components", response_model=list[Component])
async def get_components():
    headers = {'Content-Type': 'application/json','X-API-Key':COMPONENTS_SERVICE_API_KEY}
    response = requests.get("https://components-service.deta.dev/components", headers=headers)
    return response.json()
