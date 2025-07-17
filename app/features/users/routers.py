from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.core.database import db_dependency
from app.core.security import decode_token
from app.features.users.schemas import UserCreate, PasswordUpdateRequest
from app.features.users.services import create_user, update_user_password

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/users", tags=["users"])

async def get_current_user_id(cookie: str = Depends(lambda request: request.cookies.get("access_token"))) -> int:
    payload = decode_token(cookie)
    return int(payload.get("sub"))

@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register_submit(db: db_dependency,
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
):
    await create_user(db, UserCreate(email=email, full_name=full_name, password=password))
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

@router.get("/change-password")
async def change_password_page(request: Request):
    return templates.TemplateResponse("change_password.html", {"request": request})

@router.post("/change-password")
async def change_password_submit(
    db: db_dependency,
    old_password: str = Form(...),
    new_password: str = Form(...),
    user_id: int = Depends(get_current_user_id),
):
    await update_user_password(db, user_id, PasswordUpdateRequest(old_password=old_password, new_password=new_password))
    return RedirectResponse(url="/habits", status_code=status.HTTP_302_FOUND)