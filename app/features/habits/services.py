from typing import List
from fastapi import HTTPException, status
from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import db_dependency
from app.features.habits.models import Habit
from app.features.habits.schemas import HabitCreate, HabitUpdate

async def get_habit(db: db_dependency, habit_id: int, owner_id: int) -> Habit:
    res = await db.execute(select(Habit).where(Habit.id==habit_id, Habit.owner_id==owner_id))
    habit = res.scalars().first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit không tồn tại")
    return habit

async def list_habits(db: db_dependency, owner_id: int) -> List[Habit]:
    res = await db.execute(select(Habit).where(Habit.owner_id==owner_id))
    return res.scalars().all()

async def create_habit(db: db_dependency, owner_id: int, data: HabitCreate) -> Habit:
    habit = Habit(**data.dict(), owner_id=owner_id)
    db.add(habit)
    await db.commit()
    await db.refresh(habit)
    return habit

async def toggle_habit(db: db_dependency, habit_id: int, owner_id: int) -> Habit:
    habit = await get_habit(db, habit_id, owner_id)
    habit.active = not habit.active
    db.add(habit)
    await db.commit()
    await db.refresh(habit)
    return habit

async def delete_habit(db: db_dependency, habit_id: int, owner_id: int) -> None:
    habit = await get_habit(db, habit_id, owner_id)
    await db.delete(habit)
    await db.commit()