from fastapi import APIRouter, HTTPException

from app.core.schemas.group import (
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    GroupStageUpdate,
)
from app.core.services import group_service

router = APIRouter(prefix="/api/groups", tags=["groups"])


@router.get("", response_model=list[GroupResponse])
def list_groups():
    return group_service.get_all_groups()


@router.get("/{group_id}", response_model=GroupResponse)
def get_group(group_id: int):
    group = group_service.get_group(group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return group


@router.post("", response_model=GroupResponse, status_code=201)
def create_group(data: GroupCreate):
    return group_service.create_group(data)


@router.put("/{group_id}", response_model=GroupResponse)
def update_group(group_id: int, data: GroupUpdate):
    updated = group_service.update_group(group_id, data)
    if updated is None:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return updated


@router.delete("/{group_id}", status_code=204)
def delete_group(group_id: int):
    deleted = group_service.delete_group(group_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")


@router.get("/{group_id}/students")
def get_group_students(group_id: int):
    students = group_service.get_group_students(group_id)
    if students is None:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return students


@router.get("/{group_id}/meetings")
def get_group_meetings(group_id: int):
    meetings = group_service.get_group_meetings(group_id)
    if meetings is None:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return meetings


@router.get("/{group_id}/deliverables")
def get_group_deliverables(group_id: int):
    deliverables = group_service.get_group_deliverables(group_id)
    if deliverables is None:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return deliverables


@router.patch("/{group_id}/stage", response_model=GroupResponse)
def change_group_stage(group_id: int, data: GroupStageUpdate):
    updated = group_service.change_stage(group_id, data.stage_id)
    if updated is None:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return updated