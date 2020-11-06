from pydantic import BaseModel
from pathlib import Path
from enum import IntEnum


class AttachmentType(IntEnum):
    DOCUMENT = 0
    IMAGE = 1


class Attachment(BaseModel):
    filename: str
    url: str = None
    type: AttachmentType = None
