from models.custom_base_model import CustomBaseModel
from pydantic import Field,validator

class Component(CustomBaseModel):
    id: int
    name: str
    vendor: str
    price: float
    description: str
    location: str
    manufacturer: str
    product_group: str 
    weight: float
    status: str
    ean_number: str

    @validator('weight','price', pre=True)
    def empty_str_to_zero(cls, value):
        if value == '':
            return 0
        return value