from models.custom_base_model import CustomBaseModel
from pydantic import Field

class FavoritesModel(CustomBaseModel):
    key: str = Field(alias="ownerId")
    component_ids: list[str]
    product_ids: list[str]

    def __getitem__(self, item):
        return getattr(self, item)

class ToggleFavoriteModel(CustomBaseModel):
    id: str
    item_type :str

class FavoritesRequestModel(CustomBaseModel):
    key: str = Field(alias="ownerId")
