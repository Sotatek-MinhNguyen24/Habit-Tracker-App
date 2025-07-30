from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.database import lifespan, AsyncSessionLocal
from app.core.initial_data import create_admin_if_not_exists
from app.features.auth.routers import router as auth_router
from app.features.password_reset.routers import router as pr_router
from app.features.users.routers import router as users_router
from app.features.habits.routers import router as habits_router
from app.features.admin.routers import router as admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as session:
        await create_admin_if_not_exists(session)
    yield

app = FastAPI(title="Habit Tracker App", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", include_in_schema=False)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "show_nav":False})

app.include_router(auth_router)
app.include_router(pr_router)
app.include_router(users_router)
app.include_router(habits_router)
app.include_router(admin_router)