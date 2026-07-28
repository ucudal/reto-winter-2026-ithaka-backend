from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db.session import get_db

from app.core.schemas.group import (
    GroupUpsert,
    GroupResponse,
    GroupStageUpdate,
    GroupTutorsUpdate,
)
from app.core.schemas.deliverable import DeliverableRead
from app.core.security import require_authenticated, require_coordinator, require_tutor_or_coordinator
from app.core.services.group_service import GroupService

router = APIRouter(prefix="/api/groups", tags=["groups"])

def get_group_service() -> GroupService:
    return GroupService()


@router.get("", response_model=list[GroupResponse], dependencies=[Depends(require_authenticated)])
def list_groups(
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    return service.list_groups(db)


@router.get("/{group_id}", response_model=GroupResponse, dependencies=[Depends(require_authenticated)])
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    return service.get_group(db, group_id)


@router.put("", response_model=GroupResponse, dependencies=[Depends(require_coordinator)])
def upsert_group(
    data: GroupUpsert,
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    return service.upsert_group(db, data)


@router.delete("/{group_id}", status_code=204, dependencies=[Depends(require_coordinator)])
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    service.delete_group(db, group_id)


@router.patch("/{group_id}/stage", response_model=GroupResponse, dependencies=[Depends(require_tutor_or_coordinator)])
def update_group_stage(
    group_id: int,
    data: GroupStageUpdate,
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    return service.change_stage(db, group_id, data.stage_id)


@router.patch("/{group_id}/tutors", response_model=GroupResponse, dependencies=[Depends(require_coordinator)])
def update_group_tutors(
    group_id: int,
    data: GroupTutorsUpdate,
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    return service.update_tutors(db, group_id, data.business_tutor_id, data.technical_tutor_id)


@router.get("/{group_id}/students", dependencies=[Depends(require_authenticated)])
def get_group_students(
    group_id: int,
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    return service.get_group_students(db, group_id)


@router.get("/{group_id}/meetings", dependencies=[Depends(require_authenticated)])
def get_group_meetings(
    group_id: int,
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    return service.get_group_meetings(db, group_id)


@router.get("/{group_id}/deliverables", response_model=list[DeliverableRead], dependencies=[Depends(require_authenticated)])
def get_group_deliverables(
    group_id: int,
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    return service.get_group_deliverables(db, group_id)
