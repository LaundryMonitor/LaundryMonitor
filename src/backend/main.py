from fastapi import FastAPI

from backend.api.routes import router as api_router


app = FastAPI(
    title="Laundry Monitor API",
    description=(
        "Backend API for reporting laundry machine state and reading inferred "
        "current availability."
    ),
    version="0.2.0",
)

app.include_router(api_router)
