from pydantic import BaseModel
from enum import IntEnum

from .user import User


class EpicState(IntEnum):
    OPEN = 0
    CLOSED = 1


class Epic(BaseModel):
    id: int
    title: str
    description: str
    author: User

    state: EpicState = EpicState.OPEN

    created_at: float
    updated_at: float = None
    due_date: float = None
