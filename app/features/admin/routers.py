from fastapi import APIRouter, Request, Depends, status, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.features.users.models import User, UserRole
from app.features.habits.models import Habit
from app.features.users.schemas import UserProfileUpdate
from app.features.users.services import update_user_profile

router    = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/users", name="admin_list_users")
async def admin_list_users(request:Request, db:AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    res = await db.execute(select(User))
    users = res.scalars().all()
    return templates.TemplateResponse("admin/users.html",{"request":request,"current_user":current_admin, "users":users})

@router.get("/users/{user_id}/edit",name="admin_edit_user_form")
async def admin_edit_user_form(request: Request,user_id: int,db: AsyncSession = Depends(get_db),
                               current_admin: User = Depends(get_current_admin),):
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    return templates.TemplateResponse("admin/edit_user.html",{"request": request,"current_user": current_admin,"user": user})

@router.put("/users/{user_id}/edit",name="admin_edit_user",status_code=status.HTTP_303_SEE_OTHER)
async def admin_edit_user(
    request: Request,
    user_id: int,
    full_name: str = Form(None),
    phone: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()

    profile_data = UserProfileUpdate(full_name=full_name, phone=phone)
    await update_user_profile(db, user, profile_data)

    return RedirectResponse(
        url=request.url_for("admin_list_users"),
        status_code=status.HTTP_303_SEE_OTHER,
    )

@router.put("/users/{user_id}/toggle-admin",name="admin_toggle_user_role", status_code=303)
async def admin_toggle_user_role(request: Request,
                                 user_id: int, db:AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()

    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Can not change own role")

    user.role = (UserRole.user if user.role == UserRole.admin else UserRole.admin)
    await db.commit()
    return RedirectResponse(url=request.url_for("admin_list_users"),status_code=303)

@router.delete("/users/{user_id}/delete", name="admin_delete_user", status_code=303)
async def admin_delete_user (request:Request, user_id: int, db:AsyncSession=Depends(get_db), current_admin: User = Depends(get_current_admin)):
    if user_id == current_admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can not delete yourself")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user.role == UserRole.admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can not delete admin")
    await db.delete(user)
    await db.commit()

    return RedirectResponse(url=request.url_for("admin_list_users"),status_code=303)

@router.get("/habits", name="admin_list_habits")
async def admin_list_habits(request: Request, db:AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    res = await db.execute(select(Habit))
    habits = res.scalars().all()
    return templates.TemplateResponse("admin/habits.html",{"request":request, "current_user":current_admin, "habits":habits})

@router.delete("/habits/{habit_id}/delete", name="admin_delete_habits",status_code=303)
async def admin_delete_habits(request:Request, habit_id:int, db:AsyncSession = Depends(get_db), current_admin: User = Depends((get_current_admin))):
    res = await db.execute(select(Habit).where(Habit.id == habit_id))
    habit = res.scalar_one_or_none()
    await db.delete(habit)
    await db.commit()
    return RedirectResponse(url=request.url_for("admin_list_habits"), status_code=303)






