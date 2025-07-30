from typing import List
from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from dateutil.relativedelta import relativedelta

from app.features.habits.models import Habit, HabitLog, HabitFrequency
from app.features.habits.schemas import HabitCreate, HabitUpdate


def _update_streak(habit: Habit, on_date: date):
    last = habit.last_completed_date
    freq = habit.frequency

    if freq == HabitFrequency.daily:
        expected = on_date - timedelta(days=1)
        habit.current_streak = habit.current_streak + 1 if last == expected else 1

    elif freq == HabitFrequency.monthly:
        if last:
            expected = last + relativedelta(months=1)
        else:
            expected = None
        is_consecutive = expected and (on_date.year, on_date.month) == (expected.year, expected.month)
        habit.current_streak = habit.current_streak + 1 if is_consecutive else 1

    elif freq == HabitFrequency.yearly:
        if last:
            expected = last.replace(year=last.year + 1)
        else:
            expected = None
        is_consecutive = expected and (on_date.year == expected.year)
        habit.current_streak = habit.current_streak + 1 if is_consecutive else 1

    habit.last_completed_date = on_date


async def list_habits(db: AsyncSession, owner_id: int) -> List[Habit]:
    res = await db.execute(select(Habit).where(Habit.owner_id == owner_id))
    return res.scalars().all()


async def create_habit(db: AsyncSession, owner_id: int, data: HabitCreate) -> Habit:
    habit = Habit(**data.model_dump(), owner_id=owner_id)
    db.add(habit)
    await db.commit()
    await db.refresh(habit)
    return habit


async def toggle_habit(db: AsyncSession, habit_id: int, owner_id: int) -> Habit:
    res = await db.execute(
        select(Habit).where(Habit.id == habit_id, Habit.owner_id == owner_id)
    )
    habit = res.scalars().first()
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit không tồn tại"
        )
    habit.active = not habit.active
    db.add(habit)
    await db.commit()
    await db.refresh(habit)
    return habit


async def delete_habit(db: AsyncSession, habit_id: int, owner_id: int) -> None:
    res = await db.execute(
        select(Habit).where(Habit.id == habit_id, Habit.owner_id == owner_id)
    )
    habit = res.scalars().first()
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit không tồn tại"
        )
    await db.delete(habit)
    await db.commit()


async def update_habit(db: AsyncSession, habit: Habit, data: HabitUpdate) -> Habit:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(habit, field, value)
    db.add(habit)
    await db.commit()
    await db.refresh(habit)
    return habit


async def toggle_habit_log(
    db: AsyncSession,
    habit_id: int,
    owner_id: int,
    on_date: date
) -> Habit:
    res = await db.execute(
        select(Habit).where(Habit.id == habit_id, Habit.owner_id == owner_id)
    )
    habit = res.scalars().first()
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit không tồn tại"
        )

    stmt = select(HabitLog).where(
        HabitLog.habit_id == habit_id,
        HabitLog.timestamp == on_date
    )
    res = await db.execute(stmt)
    log = res.scalars().first()

    if log:
        await db.execute(delete(HabitLog).where(HabitLog.id == log.id))
        habit.current_streak = 0
        habit.last_completed_date = None
    else:
        db.add(HabitLog(habit_id=habit_id, timestamp=on_date))
        _update_streak(habit, on_date)

    db.add(habit)
    await db.commit()
    await db.refresh(habit)
    return habit
