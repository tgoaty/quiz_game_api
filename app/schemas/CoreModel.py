from pydantic import BaseModel


class CoreModel(BaseModel):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
