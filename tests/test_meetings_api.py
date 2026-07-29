from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.schemas.meeting import (
    GroupMeetingsTotalHoursRead,
    MeetingRead,
    MeetingUpsertRequest,
)
from app.core.security import (
    require_authenticated,
    require_coordinator,
    require_tutor_or_coordinator,
)
from app.core.services.meeting_service import MeetingService

router = APIRouter(
    tags=["Meetings"],
)


def get_meeting_service() -> MeetingService:
    return MeetingService()


@router.get(
    "/api/meetings",
    response_model=list[MeetingRead],
    dependencies=[Depends(require_tutor_or_coordinator)],
)
def list_meetings(
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    return service.list_meetings(db)


@router.get(
    "/api/meetings/{meeting_id}",
    response_model=MeetingRead,
    dependencies=[Depends(require_authenticated)],
)
def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    return service.get_meeting(db, meeting_id)


@router.put(
    "/api/meetings",
    response_model=MeetingRead,
    dependencies=[Depends(require_tutor_or_coordinator)],
)
def upsert_meeting(
    payload: MeetingUpsertRequest,
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    return service.upsert_meeting(db, payload)


@router.delete(
    "/api/meetings/{meeting_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_coordinator)],
)
def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    service.delete_meeting(db, meeting_id)


@router.get(
    "/api/groups/{group_id}/meetings/total-hours",
    response_model=GroupMeetingsTotalHoursRead,
    dependencies=[Depends(require_authenticated)],
)
def get_group_total_hours(
    group_id: int,
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    return service.get_group_total_hours(db, group_id)