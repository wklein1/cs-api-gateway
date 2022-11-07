from models.custom_base_model import CustomBaseModel
from pydantic import Field

class ProductModel(CustomBaseModel):
    name: str
    description: str
    component_ids: list[str]
    price: float

    def __getitem__(self, item):
        return getattr(self, item)

class ProductResponseModel(ProductModel):
    productId: str = Field(alias="id")

class ProductRequestModel(ProductModel):
    key: str = Field(alias="productId")
   
   