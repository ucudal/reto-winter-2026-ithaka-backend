from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db.session import get_db

from app.core.schemas.group import (
    GroupUpsert,
    GroupResponse
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


@router.put("", response_model=GroupResponse)
def upsert_group(
    data: GroupUpsert,
    db: Session = Depends(get_db),
    service: GroupService = Depends(get_group_service),
):
    return service.upsert_group(db, data)


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
