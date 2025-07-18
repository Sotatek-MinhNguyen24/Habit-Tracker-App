from fastapi import APIRouter, Depends, Request, BackgroundTasks, Form, status, HTTPException

from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.mail import send_reset_password_email
from app.features.password_reset.services import generate_reset_token, reset_password

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/auth", tags=["password_reset"])


@router.get("/forgot-password")
async def forgot_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})


@router.post("/forgot-password")
async def forgot_submit(background_tasks: BackgroundTasks,
                        request: Request,
                        email: str = Form(...),
                        db: AsyncSession = Depends(get_db),
                        ):
    try:
        token = await generate_reset_token(db, email)
        send_reset_password_email(email, token, background_tasks)
    except HTTPException:
        pass
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)


@router.get("/reset-password")
async def reset_page(request: Request, token: str):
    return templates.TemplateResponse("reset_password.html", {"request": request, "token": token})


@router.post("/reset-password")
async def reset_submit(
        request: Request,
        token: str = Form(...),
        new_password: str = Form(...),
        confirm_password: str = Form(...),
        db: AsyncSession = Depends(get_db),
):
    if new_password != confirm_password:
        return templates.TemplateResponse("reset_password.html",{
                "request": request,
                "token": token,
                "error": "Xác nhận mật khẩu không khớp"
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        await reset_password(db, token, new_password)
    except HTTPException as e:
        return templates.TemplateResponse(
            "reset_password.html",
            {
                "request": request,
                "token": token,
                "error": e.detail
            },
            status_code=e.status_code
        )

    return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
