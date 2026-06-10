"""FastAPI application factory and entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analytics, employees, meta
from app.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Salary Management API",
        version="0.1.0",
        description="Manage employee salary data and answer org-wide pay questions.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(meta.router)
    app.include_router(employees.router)
    app.include_router(analytics.router)
    return app


app = create_app()
