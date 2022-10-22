from pydantic import BaseModel,Extra
import modules.case_converter.case_converter as case_converter

class CustomBaseModel(BaseModel):
    class Config:
        alias_generator = case_converter.snake_to_camel_case
        allow_population_by_field_name = True
        extra = Extra.forbid