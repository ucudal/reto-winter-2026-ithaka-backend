from fastapi import HTTPException

from app.core.models.group import Group
from app.core.repositories import group_repository


def get_all_groups() -> list[Group]:
    return group_repository.get_all()


def get_group(group_id: int) -> Group:
    group = group_repository.get_by_id(group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return group


def create_group(data) -> Group:
    return group_repository.create(data)


def update_group(group_id: int, data) -> Group:
    updated = group_repository.update(group_id, data)
    if updated is None:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return updated


def delete_group(group_id: int) -> None:
    deleted = group_repository.delete(group_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")


def change_stage(group_id: int, new_stage_id: int) -> Group:
    group = group_repository.get_by_id(group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    group.current_stage_id = new_stage_id
    return group


def get_group_students(group_id: int) -> list:
    if group_repository.get_by_id(group_id) is None:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return []


def get_group_meetings(group_id: int) -> list:
    if group_repository.get_by_id(group_id) is None:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return []


def get_group_deliverables(group_id: int) -> list:
    if group_repository.get_by_id(group_id) is None:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return []