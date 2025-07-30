from fastapi import APIRouter, Depends, Request, Form, status, HTTPException
from typing import Optional

from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.core.dependencies import get_current_active_user
from app.features.users.schemas import UserCreate, PasswordUpdateRequest, UserProfileUpdate
from app.features.users.services import create_user, update_user_password, update_user_profile, get_user_profile

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/users", tags=["users"])

def get_current_user_id(request: Request) -> int:
    token = request.cookies.get("access_token")
    payload = decode_token(token)
    return int(payload.get("sub"))

@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "show_nav":False})

@router.post("/register")
async def register_submit(request: Request,email: str = Form(...),full_name: str = Form(...),password: str = Form(...), phone:str = Form(...),
                          db: AsyncSession = Depends(get_db),):
    await create_user(db, UserCreate(
        email=email, full_name=full_name, password=password, phone=phone
    ))
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

@router.get("/profile")
async def profile_page(request:Request, user = Depends(get_current_active_user), db:AsyncSession = Depends(get_db)):
    if user.role != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only user can access")
    current_user = await get_user_profile(db, user.id)
    return templates.TemplateResponse("profile.html", {"request":request, "current_user": current_user})


@router.post("/profile", status_code=status.HTTP_303_SEE_OTHER)
async def profile_update(request: Request, full_name : Optional[str]=Form(None), phone: Optional[str]=Form(None),
                         db: AsyncSession = Depends(get_db), current_user = Depends(get_current_active_user)):
    data = UserProfileUpdate(full_name=full_name, phone=phone)
    await update_user_profile(db, current_user, data)
    return RedirectResponse(request.url_for("profile_page"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/change-password")
async def change_password_page(request: Request):
    return templates.TemplateResponse("change_password.html", {"request": request, "show_nav": False})

@router.post("/change-password")
async def change_password_submit(request: Request,
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
