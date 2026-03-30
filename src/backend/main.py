from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routes import router as api_router
from backend.database import init_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    yield


app = FastAPI(
    title="Laundry Monitor API",
    description=(
        "Backend API for reporting laundry machine state and reading inferred "
        "current availability."
    ),
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(api_router)
