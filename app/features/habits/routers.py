
from datetime import date
from fastapi import APIRouter, Request, Depends, Form, status, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.features.users.models import User, UserRole
from app.features.habits.models import Habit, HabitLog
from app.features.habits.schemas import HabitCreate, HabitUpdate
from app.features.habits.services import (
    create_habit,
    update_habit,
    delete_habit,
    toggle_habit,
    toggle_habit_log,
)
from app.features.utils.periods import get_current_period

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/habits", tags=["habits"])


def _assert_owner_or_admin(habit: Habit, current_user: User):
    if current_user.role != UserRole.admin and habit.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.get("/", name="list_habits")
async def list_habits_route(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):

    stmt = select(Habit) if current_user.role == UserRole.admin else \
           select(Habit).where(Habit.owner_id == current_user.id)

    res = await db.execute(stmt)
    habits = res.scalars().all()

    header_daily = get_current_period("daily")
    header_monthly = get_current_period("monthly")
    header_yearly = get_current_period("yearly")

    daily_list, monthly_list, yearly_list = [], [], []

    for h in habits:
        header = {
            "daily": header_daily,
            "monthly": header_monthly,
            "yearly": header_yearly,
        }[h.frequency]


        logs = (await db.execute(select(HabitLog).where(HabitLog.habit_id == h.id, HabitLog.timestamp.in_(header)))).scalars().all()

        checked = {log.timestamp.isoformat() for log in logs}

        ctx = {
            "habit": h,
            "checked": checked,
            "current_streak": h.current_streak,
        }

        if h.frequency == "daily":
            daily_list.append(ctx)
        elif h.frequency == "monthly":
            monthly_list.append(ctx)
        else:
            yearly_list.append(ctx)

    return templates.TemplateResponse(
        "habits.html",
        {
            "request": request,
            "current_user": current_user,
            "header_daily": header_daily,
            "header_monthly": header_monthly,
            "header_yearly": header_yearly,
            "daily_habits": daily_list,
            "monthly_habits": monthly_list,
            "yearly_habits": yearly_list,
        },
    )


@router.post("/", status_code=status.HTTP_303_SEE_OTHER)
async def add_habit_route(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    frequency: str = Form("daily"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    await create_habit(
        db, owner_id=current_user.id, data=HabitCreate(name=name, description=description, frequency=frequency)
    )
    return RedirectResponse(request.url_for("list_habits"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{habit_id}/edit", name="edit_habit_page")
async def edit_habit_page(
    request: Request,
    habit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    res = await db.execute(select(Habit).where(Habit.id == habit_id))
    habit = res.scalars().first()
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    _assert_owner_or_admin(habit, current_user)

    return templates.TemplateResponse(
        "edit_habit.html",
        {"request": request, "current_user": current_user, "habit": habit},
    )


@router.post("/{habit_id}/edit", status_code=status.HTTP_303_SEE_OTHER)
async def edit_habit_submit(
    request: Request,
    habit_id: int,
    name: str = Form(...),
    description: str = Form(""),
    frequency: str = Form("daily"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    res = await db.execute(select(Habit).where(Habit.id == habit_id))
    habit = res.scalars().first()
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    _assert_owner_or_admin(habit, current_user)

    await update_habit(
        db,
        habit,
        data=HabitUpdate(name=name, description=description, frequency=frequency),
    )
    return RedirectResponse(request.url_for("list_habits"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{habit_id}/toggle", status_code=status.HTTP_303_SEE_OTHER)
async def toggle_active_route(
    request: Request,
    habit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    res = await db.execute(select(Habit).where(Habit.id == habit_id))
    habit = res.scalars().first()
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    _assert_owner_or_admin(habit, current_user)

    await toggle_habit(db, habit_id, current_user.id)
    return RedirectResponse(request.url_for("list_habits"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{habit_id}/delete", status_code=status.HTTP_303_SEE_OTHER)
async def delete_route(
    request: Request,
    habit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    res = await db.execute(select(Habit).where(Habit.id == habit_id))
    habit = res.scalars().first()
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    _assert_owner_or_admin(habit, current_user)

    await delete_habit(db, habit_id, current_user.id)
    return RedirectResponse(request.url_for("list_habits"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{habit_id}/check", name="check_habit", status_code=status.HTTP_302_FOUND)
async def check_habit_route(
    request: Request,
    habit_id: int,
    the_date: date = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    res = await db.execute(select(Habit).where(Habit.id == habit_id))
    habit = res.scalars().first()
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    _assert_owner_or_admin(habit, current_user)

    # pass owner_id into toggle_habit_log to update streak correctly
    await toggle_habit_log(db, habit_id, current_user.id, the_date)

    return RedirectResponse(request.url_for("list_habits"), status_code=status.HTTP_302_FOUND)
