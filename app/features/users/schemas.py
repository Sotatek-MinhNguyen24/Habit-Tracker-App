# app/features/users/schemas.py

from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    full_name: constr(min_length=1, max_length=100)
    password: constr(min_length=6)
    phone: str

class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PasswordUpdateRequest(BaseModel):
    old_password: constr(min_length=6)
    new_password: constr(min_length=6)

class UserProfileUpdate(BaseModel):
    full_name: Optional[constr(min_length=1, max_length=100)] = None
    phone: Optional[str] = None
