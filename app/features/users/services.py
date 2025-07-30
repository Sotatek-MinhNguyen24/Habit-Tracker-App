from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.core.security import get_password_hash, verify_password
from app.features.users.models import User
from app.features.users.schemas import UserCreate, PasswordUpdateRequest, UserProfileUpdate

async def get_user_by_email(
    db: AsyncSession, email: str
) -> Optional[User]:
    res = await db.execute(select(User).where(User.email == email))
    return res.scalars().first()

async def get_user_by_id(
    db: AsyncSession, user_id: int
) -> Optional[User]:
    res = await db.execute(select(User).where(User.id == user_id))
    return res.scalars().first()

async def create_user(
    db: AsyncSession, data: UserCreate
) -> User:
    if await get_user_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã tồn tại"
        )
    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=get_password_hash(data.password),
        phone=data.phone
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_user_profile(db:AsyncSession, user_id:int) ->User:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    return user

async def update_user_profile(db:AsyncSession, user:User, data:UserProfileUpdate) -> User:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user,field,value)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def update_user_password(db: AsyncSession, user_id: int, passwords: PasswordUpdateRequest) -> None:
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại")

    if not verify_password(passwords.old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Mật khẩu cũ không đúng")

    user.hashed_password = get_password_hash(passwords.new_password)
    db.add(user)
    await db.commit()


async def set_user_password(db: AsyncSession,user_id: int,new_password: str) -> None:
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    await db.commit()
