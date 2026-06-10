"""Employee CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import pagination_params
from app.core.pagination import Page, PageParams
from app.database import get_db
from app.models import EmploymentStatus
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.services import employee_service as service

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.get("", response_model=Page[EmployeeRead])
def list_employees(
    q: str | None = Query(None, description="Search by name or email"),
    country: str | None = Query(None, description="Country code"),
    department_id: int | None = Query(None),
    level: int | None = Query(None, ge=1, le=7),
    employment_status: EmploymentStatus | None = Query(None, alias="status"),
    params: PageParams = Depends(pagination_params),
    db: Session = Depends(get_db),
) -> Page[EmployeeRead]:
    return service.list_employees(
        db,
        params,
        q=q,
        country=country,
        department_id=department_id,
        level=level,
        status=employment_status,
    )


@router.post("", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)) -> EmployeeRead:
    try:
        return service.create_employee(db, payload)
    except service.ReferenceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        ) from exc


@router.get("/{employee_id}", response_model=EmployeeRead)
def get_employee(employee_id: int, db: Session = Depends(get_db)) -> EmployeeRead:
    employee = service.get_employee(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


@router.patch("/{employee_id}", response_model=EmployeeRead)
def update_employee(
    employee_id: int, payload: EmployeeUpdate, db: Session = Depends(get_db)
) -> EmployeeRead:
    try:
        return service.update_employee(db, employee_id, payload)
    except service.EmployeeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        ) from None
    except service.ReferenceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        ) from exc


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_employee(employee_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.deactivate_employee(db, employee_id)
    except service.EmployeeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        ) from None
