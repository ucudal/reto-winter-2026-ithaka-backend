from app.core.models.group import Group
from app.core.repositories import group_repository


def get_all_groups() -> list[Group]:
    return group_repository.get_all()


def get_group(group_id: int) -> Group | None:
    return group_repository.get_by_id(group_id)


def create_group(data) -> Group:
    return group_repository.create(data)


def update_group(group_id: int, data) -> Group | None:
    return group_repository.update(group_id, data)


def delete_group(group_id: int) -> bool:
    return group_repository.delete(group_id)


def change_stage(group_id: int, new_stage_id: int) -> Group | None:
    group = group_repository.get_by_id(group_id)
    if group is None:
        return None
    group.current_stage_id = new_stage_id
    return group
