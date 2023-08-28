from pydantic import BaseModel
from datetime import datetime

class ReminderCreate(BaseModel):
    title: str
    description: str
    remind_at: datetime

class ReminderDB(ReminderCreate):
    id: str
