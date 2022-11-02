from models.custom_base_model import CustomBaseModel
from pydantic import Field

class ProductModel(CustomBaseModel):
    owner_id: str
    name: str
    description: str
    component_ids: list[str]
    price: float

    def __getitem__(self, item):
        return getattr(self, item)

class ProductResponseModel(ProductModel):
    key: str = Field(alias="productId")

class ProductRequestModel(ProductModel):
    key: str = Field(alias="productId")
   
   