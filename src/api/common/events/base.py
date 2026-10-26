from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Event(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
