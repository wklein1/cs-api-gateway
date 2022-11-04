from fastapi import FastAPI, APIRouter, HTTPException, status,Header
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime,timedelta
from decouple import config
import requests
from models.component_model import Component
from models import error_models, favorites_models
from modules.jwt.jwt_module import JwtEncoder
from utils import decode_auth_token

JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITHM="HS256"
FAVORITES_SERVICE_ACCESS_KEY = config("FAVORITES_SERVICE_ACCESS_KEY")

favorites_service_jwt_encoder = JwtEncoder(secret=FAVORITES_SERVICE_ACCESS_KEY, algorithm=JWT_ALGORITHM)

router = APIRouter(
    prefix="/favorites",
    tags=["favorites microservice"]
)

@router.get(
    "",
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
   


@router.post(
    "/items",
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


@router.delete(    
     "/items",
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