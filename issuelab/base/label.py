from pydantic import BaseModel


class Label(BaseModel):
    name: str
    description: str
    color_hex: str
    priority: str = None
