from datetime import timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.core.config import RESET_PASSWORD_TOKEN_EXPIRE_HOURS
from app.core.security import create_access_token, decode_token
from app.features.users.models import User
from app.features.users.services import set_user_password

async def generate_reset_token(
    db: AsyncSession, email: str
) -> str:
    res = await db.execute(select(User).where(User.email == email))
    user = res.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="Nếu email tồn tại, bạn sẽ nhận được link"
        )

    return create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(hours=RESET_PASSWORD_TOKEN_EXPIRE_HOURS),
    )

async def reset_password(db: AsyncSession, token: str, new_password: str) -> None:
    payload = decode_token(token)
    uid = payload.get("sub")
    if not uid:
        raise HTTPException(status_code=400, detail="Token không hợp lệ")
    await set_user_password(db, int(uid), new_password)
