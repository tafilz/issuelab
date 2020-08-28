from pydantic import BaseModel


class User(BaseModel):
    id: int = -1
    name: str = ""
    username: str
    
    def __eq__(self, other):
        return self.username == other.username

    def __hash__(self):
        return hash(('username', self.username))