from models.custom_base_model import CustomBaseModel

class AuthResponseModel(CustomBaseModel):
    user_name:str
    token:str

class LoginModel(CustomBaseModel):
    user_name:str
    password:str

class PasswordInModel(CustomBaseModel):
    password:str