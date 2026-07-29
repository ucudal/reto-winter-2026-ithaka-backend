from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.models.enums import UserRole
from app.core.models.user import User
from app.core.schemas.meeting import (
    GroupMeetingsTotalHoursRead,
    MeetingRead,
    MeetingUpsertRequest,
)
from app.core.security import get_current_user, require_roles
from app.core.services.meeting_service import MeetingService

router = APIRouter(
    tags=["Meetings"],
)


def get_meeting_service() -> MeetingService:
    return MeetingService()


@router.get("/api/meetings", response_model=list[MeetingRead])
def list_meetings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    """Lista reuniones. Coordinator ve todas, tutor ve las de sus grupos, alumno ve las del suyo."""
    return service.list_meetings(db, current_user)


@router.get("/api/meetings/{meeting_id}", response_model=MeetingRead)
def get_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    """Devuelve una reunion. Solo si el usuario tiene acceso al grupo de esa reunion."""
    return service.get_meeting(db, meeting_id, current_user)


@router.put("/api/meetings", response_model=MeetingRead)
def upsert_meeting(
    payload: MeetingUpsertRequest,
    current_user: User = Depends(
        require_roles(UserRole.COORDINATOR, UserRole.BUSINESS_TUTOR, UserRole.TECHNICAL_TUTOR)
    ),
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    """Crea o actualiza una reunion. Coordinator siempre, tutor solo si es el asignado a ese grupo."""
    return service.upsert_meeting(db, payload, current_user)


@router.delete("/api/meetings/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting(
    meeting_id: int,
    current_user: User = Depends(
        require_roles(UserRole.COORDINATOR, UserRole.BUSINESS_TUTOR, UserRole.TECHNICAL_TUTOR)
    ),
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    """Elimina una reunion. Coordinator siempre, tutor solo si es el asignado a ese grupo."""
    service.delete_meeting(db, meeting_id, current_user)


@router.get(
    "/api/groups/{group_id}/meetings/total-hours",
    response_model=GroupMeetingsTotalHoursRead,
)
def get_group_total_hours(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    """Horas totales de reuniones de un grupo. Solo si el usuario tiene acceso a ese grupo."""
    return service.get_group_total_hours(db, group_id, current_user)