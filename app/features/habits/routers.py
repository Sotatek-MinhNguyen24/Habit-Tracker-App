from fastapi import APIRouter, Request, Depends, Form, status

from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import decode_token
from app.features.habits.models import Habit
from app.features.habits.schemas import HabitCreate , HabitUpdate
from app.features.habits.services import list_habits, create_habit, toggle_habit, delete_habit, update_habit

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/habits", tags=["habits"])


def get_current_user_id(request: Request) -> int:
    token = request.cookies.get("access_token")
    payload = decode_token(token)
    return int(payload.get("sub"))


@router.get("/")
async def habits_page(request: Request, db: AsyncSession = Depends(get_db)):
    uid = get_current_user_id(request)
    habits = await list_habits(db, uid)
    return templates.TemplateResponse("habits.html", {"request": request, "habits": habits})


@router.post("/")
async def add_habit(
        request: Request,
        name: str = Form(...),
        description: str = Form(""),
        frequency: str = Form("daily"),
        db: AsyncSession = Depends(get_db),
):
    uid = get_current_user_id(request)
    await create_habit(db, uid, HabitCreate(
        name=name, description=description, frequency=frequency
    ))
    return RedirectResponse(url="/habits", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{habit_id}/edit")
async def edit_habit_page(
        request: Request,
        habit_id: int,
        db: AsyncSession = Depends(get_db),
):
    uid = get_current_user_id(request)
    res = await db.execute(select(Habit).where(Habit.id == habit_id, Habit.owner_id == uid))
    habit = res.scalars().first()
    return templates.TemplateResponse("edit_habit.html", {"request": request, "habit": habit})


# Edit submit
@router.post("/{habit_id}/edit")
async def edit_habit_submit(
        request: Request,
        habit_id: int,
        name: str = Form(...),
        description: str = Form(""),
        frequency: str = Form("daily"),
        db: AsyncSession = Depends(get_db),
):
    uid = get_current_user_id(request)
    res = await db.execute(select(Habit).where(
        Habit.id == habit_id, Habit.owner_id == uid
    ))
    habit = res.scalars().first()
    await update_habit(db, habit, HabitUpdate(
        name=name,
        description=description,
        frequency=frequency
    ))
    return RedirectResponse("/habits", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{habit_id}/toggle")
async def toggle(request: Request, habit_id: int, db: AsyncSession = Depends(get_db)):
    uid = get_current_user_id(request)
    await toggle_habit(db, habit_id, uid)
    return RedirectResponse(url="/habits", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{habit_id}/delete")
async def delete(request: Request, habit_id: int, db: AsyncSession = Depends(get_db)):
    uid = get_current_user_id(request)
    await delete_habit(db, habit_id, uid)
    return RedirectResponse(url="/habits", status_code=status.HTTP_303_SEE_OTHER)
