from pydantic import BaseModel, EmailStr, constr

class UserCreate(BaseModel):
    email: EmailStr
    full_name: constr(min_length=1, max_length=100)
    password: constr(min_length=6)

class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool

    class Config:
        orm_mode = True

class PasswordUpdateRequest(BaseModel):
    old_password : constr(min_length=6)
    new_password : constr(min_length=6)