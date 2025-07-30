from enum import Enum
from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel


class HabitFrequency(str, Enum):
    daily = "daily"
    monthly = "monthly"
    yearly = "yearly"


class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None
    frequency: HabitFrequency = HabitFrequency.daily


class HabitCreate(HabitBase):
    pass


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[HabitFrequency] = None
    active: Optional[bool] = None


class HabitLogBase(BaseModel):
    timestamp: date


class HabitLogCreate(HabitLogBase):
    pass


class HabitLogRead(HabitLogBase):
    id: int
    habit_id: int

    class Config:
        orm_mode = True


class HabitRead(HabitBase):
    id: int
    active: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime
    current_streak: int
    last_completed_date: Optional[date] = None
    logs: Optional[List[HabitLogRead]] = None

    class Config:
        orm_mode = True
