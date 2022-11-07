from decouple import config
import jwt


class JwtEncoder():
    def __init__(self, secret:str, algorithm:str):
        self._jwt_secret = secret
        self. _jwt_algorithm = algorithm

    def generate_jwt(self, payload:dict):
        token = jwt.encode(payload,self._jwt_secret,self._jwt_algorithm)
        return token


    def decode_jwt(self, token:str, audience=None, issuer=None):
        try:
            decoded_token = jwt.decode(jwt=token, key = self._jwt_secret, algorithms=[self._jwt_algorithm], audience=audience, issuer=issuer ,leeway=1)
            return decoded_token 
        except Exception as ex:
            raise ex
            
    def validate_jwt(self, token:str, audience=None, issuer=None):
        try:
            decoded_token = jwt.decode(jwt=token, key = self._jwt_secret, algorithms=[self._jwt_algorithm], audience=audience, issuer=issuer, leeway=1)
            return True
        except:
            return False