from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.identity_provider import identity_provider_auth_routes, identity_provider_users_routes
from routes import product_service_routes, currency_service_routes, components_service_routes, favorites_service_routes


app = FastAPI()

app.include_router(router=identity_provider_auth_routes.router)
app.include_router(router=identity_provider_users_routes.router)
app.include_router(router=components_service_routes.router)
app.include_router(router=product_service_routes.router)
app.include_router(router=favorites_service_routes.router)
app.include_router(router=currency_service_routes.router)

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








