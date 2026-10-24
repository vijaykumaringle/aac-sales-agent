from fastapi import FastAPI

from app.api.routes import enquiries, intake


app = FastAPI(
    title="AAC Sales Agent",
    description="Captures AAC sales requirements for staff review before any quotation.",
    version="0.2.0",
)
app.include_router(enquiries.router)
app.include_router(intake.router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
