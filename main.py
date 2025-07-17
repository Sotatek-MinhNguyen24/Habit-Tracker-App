import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.database import lifespan
from app.features.auth.routers import router as auth_router
from app.features.password_reset.routers import router as pr_router
from app.features.users.routers import router as users_router
# from app.features.habits.routers import router as habits_router

app = FastAPI(title="Habit Tracker App", lifespan=lifespan)


app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth_router)
app.include_router(pr_router)
app.include_router(users_router)
# app.include_router(habits_router)