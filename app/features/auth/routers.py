from fastapi import APIRouter, Depends, Request, Form, status

from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse

from app.core.database import get_db
from app.features.auth.schemas import Token, RefreshTokenRequest
from app.features.auth.services import login_for_tokens, refresh_tokens

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login_submit(form_data: OAuth2PasswordRequestForm = Depends(),db: AsyncSession = Depends(get_db),) -> dict:
    tokens = await login_for_tokens(form_data, db)
    resp = RedirectResponse(url="/habits", status_code=status.HTTP_302_FOUND)
    resp.set_cookie("access_token", tokens["access_token"], httponly=True)
    return resp


@router.post("/token", response_model=Token)
async def token_api(db: AsyncSession = Depends(get_db),
                    form_data: OAuth2PasswordRequestForm = Depends(),
                    ):
    return await login_for_tokens(db, form_data)


@router.post("/refresh", response_model=Token)
async def refresh_api(body: RefreshTokenRequest):
    return await refresh_tokens(body)

@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response
