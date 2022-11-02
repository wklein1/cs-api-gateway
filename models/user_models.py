from models.custom_base_model import CustomBaseModel
from pydantic import Field, EmailStr, constr

PASSWORD_REGEX ="^(?=.*[A-z])(?=.*[0-9]).{8,24}$"

class UserInModel(CustomBaseModel):
    first_name:str = Field(min_length=2, max_length=24)
    last_name:str = Field(min_length=1, max_length=24)
    user_name:str = Field(min_length=3, max_length=24)
    email:EmailStr
    password:constr(regex=PASSWORD_REGEX)
    class Config:
        schema = {
            "demo":{
                "firstName":"first name",
                "lastName":"last name",
                "userName":"user_name",
                "email":"email@mail.com",
                "password":"123"
            }
        }

class UserOutModel(CustomBaseModel):
    first_name:str
    last_name:str
    user_name:str
    email:EmailStr
    class Config:
        schema = {
            "demo":{
                "firstName":"first name",
                "lastName":"last name",
                "userName":"user name",
                "email":"email@mail.com",
                "password":"123"
            }
        }

class UserUpdatesInModel(CustomBaseModel):
    first_name:str = Field(min_length=2, max_length=24)
    last_name:str = Field(min_length=1, max_length=24)
    user_name:str = Field(min_length=3, max_length=24)
    email:EmailStr
    password:str
    class Config:
        schema = {
            "demo":{
                "firstName":"first name",
                "lastName":"last name",
                "userName":"user_name",
                "email":"email@mail.com",
                "password":"123"
            }
        }

class UserNameInModel(CustomBaseModel):
    user_name:str
    

class UserNameIsTakenModel(CustomBaseModel):
    is_taken:bool

class UserChangePasswordInModel(CustomBaseModel):
    password:str
    new_password:constr(regex=PASSWORD_REGEX)
    