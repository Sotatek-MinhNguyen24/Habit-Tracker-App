from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from app.core.config import RESET_PASSWORD_TOKEN_EXPIRE_HOURS
from app.core.security import create_access_token, decode_token
from app.features.users.models import User
from app.features.users.services import update_user_password
from app.core.database import db_dependency
async def generate_reset_token(db:db_dependency, email: str) -> str:
    res = await db.execute(select(User).where(User.email == email))
    user = res.scalar().first()
    if not user:
        raise HTTPException(status_code=200, detail="Nếu email tồn tại, bạn sẽ nhận được mail")
    return create_access_token(subject=str(user.id), expires_delta=timedelta(hours=RESET_PASSWORD_TOKEN_EXPIRE_HOURS))

async def reset_password(db: db_dependency, token: str, new_password: str) -> None:
    payload = decode_token(token)
    uid = payload.get("sub")
    if not uid:
        raise HTTPException(status_code=400, detail="Token không hợp lệ")
    await update_user_password(db, int(uid), type("P", (), {"old_password":"", "new_password":new_password}))
