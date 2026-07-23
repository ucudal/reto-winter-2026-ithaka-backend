from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.schemas.meeting import GroupMeetingsTotalHoursRead, MeetingRead, MeetingUpdateRequest

from app.core.services.meeting_service import MeetingService

router = APIRouter(
    tags=["Meetings"],
)


def get_meeting_service() -> MeetingService:
    return MeetingService()


@router.get("/api/meetings", response_model=list[MeetingRead])
def list_meetings(
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    return service.list_meetings(db)


@router.get("/api/meetings/{meeting_id}", response_model=MeetingRead)
def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    return service.get_meeting(db, meeting_id)


@router.put("/api/meetings/{meeting_id}", response_model=MeetingRead)
def update_meeting(
    meeting_id: int,
    payload: MeetingUpdateRequest,
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    return service.update_meeting(db, meeting_id, payload)


@router.delete("/api/meetings/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    service.delete_meeting(db, meeting_id)


@router.get(
    "/api/groups/{group_id}/meetings/total-hours",
    response_model=GroupMeetingsTotalHoursRead,
)
def get_group_total_hours(
    group_id: int,
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    return service.get_group_total_hours(db, group_id)