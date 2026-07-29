from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.models.user import User
from app.core.schemas.meeting import (
    GroupMeetingsTotalHoursRead,
    MeetingRead,
    MeetingUpsertRequest,
)
from app.core.security import get_current_user, require_tutor_or_coordinator
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
    """Lista reuniones. El service filtra por acceso al grupo de cada reunion."""
    return service.list_meetings(db, current_user)


@router.get("/api/meetings/{meeting_id}", response_model=MeetingRead)
def get_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    """Devuelve una reunion. 403 si el usuario no tiene acceso a ese grupo."""
    return service.get_meeting(db, meeting_id, current_user)


@router.put(
    "/api/meetings",
    response_model=MeetingRead,
    dependencies=[Depends(require_tutor_or_coordinator)],
)
def upsert_meeting(
    payload: MeetingUpsertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    """Crea o actualiza una reunion. Solo Coordinator o el tutor de ese grupo."""
    return service.upsert_meeting(db, payload, current_user)


@router.delete(
    "/api/meetings/{meeting_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_tutor_or_coordinator)],
)
def delete_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    """Borra una reunion. Solo Coordinator o el tutor de ese grupo."""
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
    """Horas consumidas por el grupo. 403 si el usuario no tiene acceso al grupo."""
    return service.get_group_total_hours(db, group_id, current_user)