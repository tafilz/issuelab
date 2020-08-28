from pydantic import BaseModel


class User(BaseModel):
    id: int = -1
    name: str = ""
    username: str
