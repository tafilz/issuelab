from pydantic import BaseModel
from typing import List
from enum import IntEnum

from .label import Label
from .user import User
from .attachment import Attachment
from .comment import Comment


class IssueState(IntEnum):
    OPEN = 0
    CLOSED = 1
    LOCKED = 2


class Issue(BaseModel):
    id: int
    title: str
    description: str
    author: User
    labels: List[Label] = []
    attachments: List[Attachment] = []

    state: IssueState = IssueState.OPEN
    
    comments: List[Comment] = []

    created_at: float
    updated_at: float = None
    due_date: float = None

    assignees: List[User] = None
    milestone_id: int = None
    epic_id: int = None
    
    estimation: int = None
    time_spent: int = None
