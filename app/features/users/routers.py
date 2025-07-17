from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import db_dependency
from app.features.users.schemas import UserCreate, UserRead
from app.features.users.services import create_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: db_dependency) -> UserRead:
    return await create_user(db, user_in)


