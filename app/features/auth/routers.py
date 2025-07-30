from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.auth.schemas import Token, RefreshTokenRequest
from app.features.auth.services import login_for_tokens, refresh_tokens

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "show_nav":False})


@router.post("/login")
async def login_submit(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db),
):
    tokens = await login_for_tokens(form_data, db)
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    payload = tokens.get("payload", {})

    role = payload.get("role")
    redirect_to = "/admin/habits" if role == "admin" else "/habits"
    response = RedirectResponse(url=redirect_to, status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax")
    response.set_cookie(key="refresh_token", value=refresh_token, secure=False, samesite="lax")
    response.set_cookie(key="user_role",value=payload.get("role", ""),secure=False,samesite="lax")
    return response


@router.post("/token", response_model=Token)
async def token_api(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db),
):
    return await login_for_tokens(form_data, db)


@router.post("/refresh", response_model=Token)
async def refresh_api(body: RefreshTokenRequest):
    return await refresh_tokens(body)


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login",status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("user_role")
    return response
