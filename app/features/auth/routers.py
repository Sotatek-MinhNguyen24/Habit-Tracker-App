from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.core.database import db_dependency
from app.features.auth.schemas import Token, RefreshTokenRequest
from app.features.auth.services import login_for_tokens, refresh_tokens

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(db: db_dependency,form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    return await login_for_tokens(db, form_data)

@router.post("/refresh", response_model=Token)
async def refresh(body: RefreshTokenRequest) -> Token:
    return await refresh_tokens(body)