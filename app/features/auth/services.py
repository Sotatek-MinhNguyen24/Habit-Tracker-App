from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import (
    verify_password, create_access_token, create_refresh_token, decode_token,
)
from app.features.users.models import User
from app.features.auth.schemas import RefreshTokenRequest

async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    res = await db.execute(select(User).where(User.email == email))
    user = res.scalars().first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def login_for_tokens(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Sai email hoặc mật khẩu")
    return {
        "access_token":  create_access_token(str(user.id)),
        "refresh_token": create_refresh_token(str(user.id)),
        "token_type":    "bearer",
    }

async def refresh_tokens(body: RefreshTokenRequest) -> Token:
    payload = decode_token(body.refresh_token)
    uid = payload.get("sub")
    if not uid:
        raise HTTPException(status_code=400, detail="Refresh token không hợp lệ")
    return {
        "access_token":  create_access_token(uid),
        "refresh_token": create_refresh_token(uid),
        "token_type":    "bearer",
    }