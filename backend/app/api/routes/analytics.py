"""Analytics endpoints answering org-wide pay questions."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.analytics import DistributionOut, GroupedOut, SummaryOut
from app.services import analytics_service as service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary", response_model=SummaryOut)
def summary(db: Session = Depends(get_db)) -> SummaryOut:
    return service.get_summary(db)


@router.get("/by-country", response_model=GroupedOut)
def by_country(db: Session = Depends(get_db)) -> GroupedOut:
    return service.get_by_country(db)


@router.get("/by-department", response_model=GroupedOut)
def by_department(db: Session = Depends(get_db)) -> GroupedOut:
    return service.get_by_department(db)


@router.get("/distribution", response_model=DistributionOut)
def distribution(db: Session = Depends(get_db)) -> DistributionOut:
    return service.get_distribution(db)
