from decouple import config
from modules.jwt.jwt_module import JwtEncoder

JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITHM="HS256"
JWT_AUDIENCE="kbe-aw2022-frontend.netlify.app"
JWT_ISSUER="cs-identity-provider.deta.dev"

jwt_encoder = JwtEncoder(secret=JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_auth_token(token:str):
    try:
        return jwt_encoder.decode_jwt(token=token,audience=JWT_AUDIENCE,issuer=JWT_ISSUER)
    except:
        return None