from fastapi import FastAPI

from app.api.routes_companies import router as companies_router
from app.api.routes_health import router as health_router
from app.api.routes_tasks import router as tasks_router
from app.database import init_db
from app.logging_config import configure_logging

configure_logging()

app = FastAPI(
    title="SI Research Agent",
    description="Cloud-deployable Systems Integrator lead research API.",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(health_router)
app.include_router(tasks_router)
app.include_router(companies_router)

