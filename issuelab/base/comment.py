from pydantic import BaseModel
from typing import List

from .user import User
from .attachment import Attachment


class Comment(BaseModel):
    author: User
    text: str
    attachments: List[Attachment] = []
