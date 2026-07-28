from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db.session import get_db

from app.core.models.enums import UserRole
from app.core.models.user import User
from app.core.schemas.group import (
    GroupUpsert,
    GroupResponse,
    GroupStageUpdate,
    GroupTutorsUpdate,
)
from app.core.schemas.deliverable import DeliverableRead
from app.core.security import get_current_user, require_roles
from app.core.services.group_service import GroupService

router = APIRouter(prefix="/api/groups", tags=["groups"])

def get_group_service() -> GroupService:
    return GroupService()


@router.get("", response_model=list[GroupResponse])
def list_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    """Lista grupos. Coordinator ve todos, tutor ve los suyos, alumno ve el propio."""
    return service.list_groups(db, current_user)


@router.get("/{group_id}", response_model=GroupResponse)
def get_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    """Devuelve un grupo. Solo si el usuario tiene acceso a ese grupo puntual."""
    return service.get_group(db, group_id, current_user)


@router.put("", response_model=GroupResponse)
def upsert_group(
    data: GroupUpsert,
    _: User = Depends(require_roles(UserRole.COORDINATOR)),
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    """Crea o actualiza un grupo. Solo para Coordinator."""
    return service.upsert_group(db, data)


@router.delete("/{group_id}", status_code=204)
def delete_group(
    group_id: int,
    _: User = Depends(require_roles(UserRole.COORDINATOR)),
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    """Elimina un grupo. Solo para Coordinator."""
    service.delete_group(db, group_id)


@router.patch("/{group_id}/stage", response_model=GroupResponse)
def update_group_stage(
    group_id: int,
    data: GroupStageUpdate,
    current_user: User = Depends(
        require_roles(UserRole.COORDINATOR, UserRole.BUSINESS_TUTOR, UserRole.TECHNICAL_TUTOR)
    ),
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    """Avanza la etapa de un grupo. Coordinator siempre, tutor solo si es el asignado a ese grupo."""
    return service.change_stage(db, group_id, data.stage_id, current_user)


@router.patch("/{group_id}/tutors", response_model=GroupResponse)
def update_group_tutors(
    group_id: int,
    data: GroupTutorsUpdate,
    _: User = Depends(require_roles(UserRole.COORDINATOR)),
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    """Asigna tutores a un grupo. Solo para Coordinator."""
    return service.update_tutors(db, group_id, data.business_tutor_id, data.technical_tutor_id)


@router.get("/{group_id}/students")
def get_group_students(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    """Lista alumnos del grupo. Solo si el usuario tiene acceso a ese grupo puntual."""
    return service.get_group_students(db, group_id, current_user)


@router.get("/{group_id}/meetings")
def get_group_meetings(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    """Lista reuniones del grupo. Solo si el usuario tiene acceso a ese grupo puntual."""
    return service.get_group_meetings(db, group_id, current_user)


@router.get("/{group_id}/deliverables", response_model=list[DeliverableRead])
def get_group_deliverables(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    """Lista entregables del grupo. Solo si el usuario tiene acceso a ese grupo puntual."""
    return service.get_group_deliverables(db, group_id, current_user)
