from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from thinga.database import Base, engine
from thinga.routers import user_management, image_comparison
from thinga.config import MEDIA_STORAGE_PATH


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Thinga",
    summary="Compare and rate.",
    version="v1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/media",
    StaticFiles(directory=MEDIA_STORAGE_PATH),
    name="media",
)

app.include_router(user_management.router, tags=["User Management"])
app.include_router(image_comparison.router, tags=["Images and Ratings"])
