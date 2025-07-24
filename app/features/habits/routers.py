from datetime import date
from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import decode_token
from app.features.habits.models import Habit, HabitLog
from app.features.habits.schemas import HabitCreate, HabitUpdate
from app.features.habits.services import (
    create_habit,
    update_habit,
    delete_habit,
    toggle_habit,
    toggle_habit_log
)
from app.features.utils.periods import get_current_period

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/habits", tags=["habits"])


def get_current_user_id(request: Request) -> int:
    token = request.cookies.get("access_token") or ""
    return int(decode_token(token)["sub"])


@router.get("/", name="list_habits")
async def list_habits_route(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    # 1. Lấy tất cả habits
    res = await db.execute(select(Habit).where(Habit.owner_id == user_id))
    habits = res.scalars().all()

    # 2. Tạo header arrays (chung cho tất cả habits trong cùng frequency)
    header_daily   = get_current_period("daily")
    header_monthly = get_current_period("monthly")
    header_yearly  = get_current_period("yearly")

    # 3. Nhóm habits + build checked set
    daily_list, monthly_list, yearly_list = [], [], []

    for h in habits:
        # pick đúng header tùy h.frequency
        header = {
            "daily":   header_daily,
            "monthly": header_monthly,
            "yearly":  header_yearly
        }[h.frequency]

        # lấy logs cho đúng tập header dates
        stmt = select(HabitLog).where(
            HabitLog.habit_id == h.id,
            HabitLog.timestamp.in_(header)
        )
        logs = (await db.execute(stmt)).scalars().all()
        # checked dưới dạng chuỗi ISO để so sánh trong template
        checked = {log.timestamp.isoformat() for log in logs}

        ctx = {"habit": h, "checked": checked}

        if h.frequency == "daily":
            daily_list.append(ctx)
        elif h.frequency == "monthly":
            monthly_list.append(ctx)
        else:
            yearly_list.append(ctx)

    return templates.TemplateResponse("habits.html", {
        "request": request,
        "header_daily":   header_daily,
        "header_monthly": header_monthly,
        "header_yearly":  header_yearly,
        "daily_habits":   daily_list,
        "monthly_habits": monthly_list,
        "yearly_habits":  yearly_list,
    })


@router.post("/", status_code=status.HTTP_303_SEE_OTHER)
async def add_habit_route(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    frequency: str = Form("daily"),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    await create_habit(
        db, user_id,
        HabitCreate(name=name, description=description, frequency=frequency)
    )
    return RedirectResponse(request.url_for("list_habits"), status_code=303)


@router.get("/{habit_id}/edit", name="edit_habit_page")
async def edit_habit_page(
    request: Request,
    habit_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    res = await db.execute(
        select(Habit).where(Habit.id == habit_id, Habit.owner_id == user_id)
    )
    habit = res.scalars().first()
    return templates.TemplateResponse("edit_habit.html", {
        "request": request, "habit": habit
    })


@router.post("/{habit_id}/edit", status_code=status.HTTP_303_SEE_OTHER)
async def edit_habit_submit(
    request: Request,
    habit_id: int,
    name: str = Form(...),
    description: str = Form(""),
    frequency: str = Form("daily"),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    await update_habit(
        db, habit_id, user_id,
        HabitUpdate(name=name, description=description, frequency=frequency)
    )
    return RedirectResponse(request.url_for("list_habits"), status_code=303)


@router.post("/{habit_id}/toggle", status_code=status.HTTP_303_SEE_OTHER)
async def toggle_active_route(
    request: Request,
    habit_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    await toggle_habit(db, habit_id, user_id)
    return RedirectResponse(request.url_for("list_habits"), status_code=303)


@router.post("/{habit_id}/delete", status_code=status.HTTP_303_SEE_OTHER)
async def delete_route(
    request: Request,
    habit_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    await delete_habit(db, habit_id, user_id)
    return RedirectResponse(request.url_for("list_habits"), status_code=303)


@router.post("/{habit_id}/check", name="check_habit", status_code=status.HTTP_302_FOUND)
async def check_habit_route(
    request: Request,
    habit_id: int,
    the_date: date = Form(...),
    db: AsyncSession = Depends(get_db),
):
    await toggle_habit_log(db, habit_id, the_date)
    return RedirectResponse(request.url_for("list_habits"), status_code=302)
