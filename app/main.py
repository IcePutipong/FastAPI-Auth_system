from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers.routers_auth import router as auth_router
from db.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    print("Start...")

    yield
    print("Server shutting down...")

app=FastAPI(lifespan=lifespan)

app.include_router(auth_router)