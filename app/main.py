from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

from app.api.routers.auth import router as auth_router
from app.api.routers.catalog import router as catalog_router

from app.core.config import settings
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Store Backend", lifespan=lifespan)

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(catalog_router)

app.include_router(api_router)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
def root():
    return {"message": "Hello"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
