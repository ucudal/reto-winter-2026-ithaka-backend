from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db.session import get_db

from app.core.schemas.group import (
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    GroupStageUpdate,
)
from app.core.services.group_service import GroupService

router = APIRouter(prefix="/api/groups", tags=["groups"])

def get_group_service() -> GroupService:
    return GroupService()


@router.get("", response_model=list[GroupResponse])
def list_groups(
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    return service.list_groups(db)


@router.get("/{group_id}", response_model=GroupResponse)
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    return service.get_group(db, group_id)


@router.post("", response_model=GroupResponse, status_code=201)
def create_group(
    data: GroupCreate,
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    return service.create_group(db, data)


@router.put("/{group_id}", response_model=GroupResponse)
def update_group(
    group_id: int,
    data: GroupUpdate,
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    return service.update_group(db, group_id, data)


@router.delete("/{group_id}", status_code=204)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    service.delete_group(db, group_id)


@router.get("/{group_id}/students")
def get_group_students(
    group_id: int,
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    return service.get_group_students(db, group_id)


@router.get("/{group_id}/meetings")
def get_group_meetings(
    group_id: int,
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    return service.get_group_meetings(db, group_id)


@router.get("/{group_id}/deliverables")
def get_group_deliverables(
    group_id: int,
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    return service.get_group_deliverables(db, group_id)


@router.patch("/{group_id}/stage", response_model=GroupResponse)
def change_group_stage(
    group_id: int,
    data: GroupStageUpdate,
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    return service.change_stage(db, group_id, data.stage_id)


