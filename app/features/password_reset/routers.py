from fastapi import APIRouter,BackgroundTasks, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.core.database import db_dependency
from app.core.mail import send_reset_password_email
from app.features.password_reset.services import generate_reset_token, reset_password

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/auth", tags=["password_reset"])

@router.get("/forgot-password")
async def forgot_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@router.post("/forgot-password")
async def forgot_submit(db: db_dependency,
    background_tasks: BackgroundTasks,
    email: str = Form(...),
):
    try:
        token = await generate_reset_token(db, email)
        send_reset_password_email(email, token, background_tasks)
    except:
        pass
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

@router.get("/reset-password")
async def reset_page(request: Request, token: str):
    return templates.TemplateResponse("reset_password.html", {"request": request, "token": token})

@router.post("/reset-password")
async def reset_submit(db: db_dependency,
    token: str = Form(...),
    new_password: str = Form(...),
):
    await reset_password(db, token, new_password)
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)