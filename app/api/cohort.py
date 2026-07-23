from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.schemas.cohort import CohortRead, CohortGroupRead, CohortStageRead, CohortUpsertRequest
from app.core.services.cohort_service import CohortService

router = APIRouter(
    prefix="/api/cohorts",
    tags=["Cohorts"],
)


def get_cohort_service() -> CohortService:
    return CohortService()


@router.get("", response_model=list[CohortRead])
def list_cohorts(
    year: int | None = None,
    semester: int | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    service: CohortService = Depends(get_cohort_service),
):
    return service.list_cohorts(db, year=year, semester=semester, status=status, page=page, page_size=page_size)


@router.get("/{cohort_id}", response_model=CohortRead)
def get_cohort(
    cohort_id: int,
    db: Session = Depends(get_db),
    service: CohortService = Depends(get_cohort_service),
):
    return service.get_cohort(db, cohort_id)


@router.put("", response_model=CohortRead)
def upsert_cohort(
    payload: CohortUpsertRequest,
    db: Session = Depends(get_db),
    service: CohortService = Depends(get_cohort_service),
):
    return service.upsert_cohort(db, payload)


@router.get("/{cohort_id}/groups", response_model=list[CohortGroupRead])
def list_groups(
    cohort_id: int,
    db: Session = Depends(get_db),
    service: CohortService = Depends(get_cohort_service),
):
    return service.list_groups(db, cohort_id)


@router.get("/{cohort_id}/stages", response_model=list[CohortStageRead])
def list_stages(
    cohort_id: int,
    db: Session = Depends(get_db),
    service: CohortService = Depends(get_cohort_service),
):
    return service.list_stages(db, cohort_id)
