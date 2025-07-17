from typing import Optional
from sqlalchemy import select
from fastapi import HTTPException, status
from app.core.security import get_password_hash, verify_password
from app.features.users.models import User
from app.features.users.schemas import UserCreate, PasswordUpdateRequest
from app.core.database import db_dependency



async def get_user_by_email(db: db_dependency, email:str)-> Optional[User]:
    res = await db.execute(select(User).where(User.email == email))
    return res.scalar()

async def create_user(db:db_dependency, data:UserCreate) -> User:
    if await get_user_by_email(db, data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email đã tồn tại")
    user = User(
        email = data.email,
        full_name = data.full_name,
        hashed_password = get_password_hash(data.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_id(db:db_dependency, user_id: int) -> Optional[User]:
    res = await db.excute(select(User).where(User.id == user_id))
    return res.scalar()

async def update_user_password(db:db_dependency, user_id:int, passwords: PasswordUpdateRequest) -> None:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại")
    if not verify_password(passwords.old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Mật khẩu cũ không đúng")
    user.hashed_password = get_password_hash(passwords.new_password)
    db.add(User)
    await db.commit()
