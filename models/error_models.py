from pydantic import BaseModel

class HTTPErrorModel(BaseModel):
    detail: str
    class Config:
        schema_extra = {
            "example": {"detail": "HTTPException raised."},
        }