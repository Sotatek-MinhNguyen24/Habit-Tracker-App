from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class HabitBase(BaseModel):
    name:        str
    description: Optional[str] = None
    frequency:   Optional[str] = "daily"

class HabitCreate(HabitBase):
    pass

class HabitUpdate(BaseModel):
    name:        Optional[str]
    description: Optional[str]
    frequency:   Optional[str]
    active:      Optional[bool]

class HabitRead(HabitBase):
    id:          int
    active:      bool
    owner_id:    int
    created_at:  datetime
    updated_at:  datetime

    class Config:
        orm_mode = True