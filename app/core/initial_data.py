import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from app.core.database import get_db
from app.core.security import get_password_hash
from app.features.users.models import UserRole, User

async def create_admin_if_not_exists(db:AsyncSession = Depends(get_db)):
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    full_name = os.getenv("ADMIN_FULL_NAME", "Admin")

    if not email and not password:
        return
    res = await db.execute(select(User).where(User.email == email))
    existing = res.scalar_one_or_none()
    if existing:
        return

    admin = User(email=email, full_name=full_name, hashed_password=get_password_hash(password), role=UserRole.admin.value)
    db.add(admin)
    await db.commit()