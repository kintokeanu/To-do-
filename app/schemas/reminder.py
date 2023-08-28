from pydantic import BaseModel
from datetime import datetime
class ReminderBase(BaseModel):
    title: str
    description: str
    remind_at: datetime

class ReminderCreate(ReminderBase):
    isReminded: bool = False


class ReminderUpdate(ReminderBase):
    pass


class Reminder(ReminderBase):
    id: str
    isReminded: bool = False
