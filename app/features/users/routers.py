from fastapi import APIRouter, Depends, Request, Form, status, HTTPException

from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.features.users.schemas import UserCreate, PasswordUpdateRequest
from app.features.users.services import create_user, update_user_password

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/users", tags=["users"])

def get_current_user_id(request: Request) -> int:
    token = request.cookies.get("access_token")
    payload = decode_token(token)
    return int(payload.get("sub"))

@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register_submit(
    request: Request,
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    await create_user(db, UserCreate(
        email=email, full_name=full_name, password=password
    ))
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

@router.get("/change-password")
async def change_password_page(request: Request):
    return templates.TemplateResponse("change_password.html", {"request": request})

@router.post("/change-password")
async def change_password_submit(
    request: Request,
    old_password: str        = Form(...),
    new_password: str        = Form(...),
    confirm_password: str    = Form(...),
    db: AsyncSession         = Depends(get_db),
    user_id: int             = Depends(get_current_user_id),
):
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "change_password.html",{"request": request,"error": "Xác nhận mật khẩu không khớp"},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    try:
        await update_user_password(db,user_id,PasswordUpdateRequest(old_password=old_password, new_password=new_password))
    except HTTPException as e:
        return templates.TemplateResponse("change_password.html",{"request": request,"error": e.detail},
            status_code=e.status_code
        )
    response = RedirectResponse(url="/habits", status_code=status.HTTP_302_FOUND)
    return response
