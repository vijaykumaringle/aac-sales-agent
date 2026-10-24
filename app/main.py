from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import enquiries, intake
from app.db.sqlite import initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="AAC Sales Agent",
    description="Captures AAC sales requirements for staff review before any quotation.",
    version="0.2.0",
    lifespan=lifespan,
)
app.include_router(enquiries.router)
app.include_router(intake.router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
