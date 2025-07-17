from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.security import get_password_hash
from app.features.users.models import User
from app.features.users.schemas import UserCreate
from app.core.database import db_dependency



async def get_user_by_email(db: db_dependency, email:str)-> Optional[User]:
    res = await db.execute(select(User).where(User.email == email))
    return res.scalar().first()

async def create_user(db:db_dependency, data:UserCreate) -> User:
    if await get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email đã tồn tại")
    user = User(
        email = data.email,
        full_name = data.full_name,
        hashed_password = get_password_hash(data.password)
    )

