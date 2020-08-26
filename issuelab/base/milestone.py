from enum import IntEnum
from pydantic import BaseModel


class MilestoneState(IntEnum):
    ACTIVE = 0
    CLOSED = 1


class Milestone(BaseModel):
    id: int
    title: str
    description: str
    state: MilestoneState = MilestoneState.ACTIVE

    start_date: float = None
    due_date: float = None
