from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.models.enums import UserRole
from app.core.models.user import User
from app.core.schemas.cohort import CohortRead, CohortGroupRead, CohortStageRead, CohortUpsertRequest
from app.core.security import get_current_user, require_roles
from app.core.services.cohort_service import CohortService

router = APIRouter(
    prefix="/api/cohorts",
    tags=["Cohorts"],
)


def get_cohort_service() -> CohortService:
    return CohortService()


@router.get("", response_model=list[CohortRead])
def list_cohorts(
    year: int | None = Query(None),
    semester: int | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: CohortService = Depends(get_cohort_service),
):
    """Lista cohortes. Requiere estar autenticado."""
    return service.list_cohorts(db, year=year, semester=semester, status=status, page=page, page_size=page_size)


@router.get("/{cohort_id}", response_model=CohortRead)
def get_cohort(
    cohort_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: CohortService = Depends(get_cohort_service),
):
    """Devuelve un cohorte. Requiere estar autenticado."""
    return service.get_cohort(db, cohort_id)


@router.put("", response_model=CohortRead)
def upsert_cohort(
    payload: CohortUpsertRequest,
    _: User = Depends(require_roles(UserRole.COORDINATOR)),
    db: Session = Depends(get_db),
    service: CohortService = Depends(get_cohort_service),
):
    """Crea o actualiza un cohorte. Solo para Coordinator."""
    return service.upsert_cohort(db, payload)


@router.get("/{cohort_id}/groups", response_model=list[CohortGroupRead])
def list_groups(
    cohort_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: CohortService = Depends(get_cohort_service),
):
    """Lista los grupos de un cohorte. Coordinator ve todos, tutor ve los suyos, alumno ve solo el propio."""
    return service.list_groups(db, cohort_id, current_user)


@router.get("/{cohort_id}/stages", response_model=list[CohortStageRead])
def list_stages(
    cohort_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: CohortService = Depends(get_cohort_service),
):
    """Lista las etapas de un cohorte. Requiere estar autenticado."""
    return service.list_stages(db, cohort_id)
