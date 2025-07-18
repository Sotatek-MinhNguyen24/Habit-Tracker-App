from typing import List
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.habits.models import Habit
from app.features.habits.schemas import HabitCreate, HabitUpdate


async def list_habits(db: AsyncSession, owner_id: int) -> List[Habit]:
    res = await db.execute(select(Habit).where(Habit.owner_id == owner_id))
    return res.scalars().all()

async def create_habit(
    db: AsyncSession, owner_id: int, data: HabitCreate
) -> Habit:
    habit = Habit(**data.model_dump(), owner_id=owner_id)
    db.add(habit)
    await db.commit()
    await db.refresh(habit)
    return habit

async def toggle_habit(
    db: AsyncSession, habit_id: int, owner_id: int
) -> Habit:
    res = await db.execute(
        select(Habit).where(Habit.id==habit_id, Habit.owner_id==owner_id)
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

async def delete_habit(
    db: AsyncSession, habit_id: int, owner_id: int
) -> None:
    res = await db.execute(
        select(Habit).where(Habit.id==habit_id, Habit.owner_id==owner_id)
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

