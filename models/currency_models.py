from pydantic import Field
from models.custom_base_model import CustomBaseModel

class CurrencyModel(CustomBaseModel):
    key: str = Field(alias="code")
    symbol: str
    name: str
    country: str

class ExchangeRateResponseModel(CustomBaseModel):
    exchange_rate: float