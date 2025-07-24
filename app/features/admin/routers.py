from fastapi import APIRouter, Request, Depends, status, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.features.users.models import User, UserRole
from app.features.habits.models import Habit

router    = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/users", name="admin_list_users")
async def admin_list_users(request:Request, db:AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    res = await db.execute(select(User))
    users = res.scalars().all()
    return templates.TemplateResponse("admin/users.html",{"request":request,"current_user":current_admin, "users":users})

@router.post("/users/{user_id}/toggle-admin", status_code=303)
async def admin_toggle_user_role(request: Request,
                                 user_id: int, db:AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Can not change own role")

    user.role = (UserRole.user if user.role == UserRole.admin else UserRole.admin)
    await db.commit()
    return RedirectResponse(url=request.url_for("admin_list_users"),status_code=303)

@router.get("/habits", name="admin_list_habits")
async def admin_list_habits(request: Request, db:AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    res = await db.execute(select(Habit))
    habits = res.scalars().all()
    return templates.TemplateResponse("admin/habits.html",{"request":request, "current_user":current_admin, "habits":habits})

@router.post("/habits/{habit_id}/delete", name="admin_delete_habits",status_code=303)
async def admin_delete_habits(request:Request, habit_id:int, db:AsyncSession = Depends(get_db), current_admin: User = Depends((get_current_admin))):
    res = await db.execute(select(Habit).where(Habit.id == habit_id))
    habit = res.scalars().first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    await db.delete(habit)
    await db.commit()
    return RedirectResponse(url=request.url_for("admin_list_habits"), status_code=303)




