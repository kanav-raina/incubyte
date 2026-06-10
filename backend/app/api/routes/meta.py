"""Meta endpoints: health check and reference data for filters."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Country, Department
from app.schemas.common import CountryOut, DepartmentOut

router = APIRouter(tags=["meta"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


@router.get("/api/meta/countries", response_model=list[CountryOut])
def list_countries(db: Session = Depends(get_db)) -> list[Country]:
    return list(db.execute(select(Country).order_by(Country.name)).scalars().all())


@router.get("/api/meta/departments", response_model=list[DepartmentOut])
def list_departments(db: Session = Depends(get_db)) -> list[Department]:
    return list(db.execute(select(Department).order_by(Department.name)).scalars().all())
