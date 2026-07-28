from __future__ import annotations

from app.core.models.enums import UserRole
from app.core.models.group import Group
from app.core.models.user import User


def user_can_access_group(group: Group, user: User) -> bool:
    """Determina si `user` tiene permiso para ver/operar sobre `group`.

    - Coordinator: siempre.
    - BusinessTutor/TechnicalTutor: solo si es el tutor asignado a ese grupo.
    - Student: solo si pertenece a ese grupo.
    """
    if user.role == UserRole.COORDINATOR:
        return True

    if user.role in (UserRole.BUSINESS_TUTOR, UserRole.TECHNICAL_TUTOR):
        return (
            (group.business_tutor and group.business_tutor.user_id == user.id)
            or (group.technical_tutor and group.technical_tutor.user_id == user.id)
        )

    if user.role == UserRole.STUDENT:
        return any(student.user_id == user.id for student in group.students)

    return False


def filter_groups_for_user(groups: list[Group], user: User) -> list[Group]:
    """Filtra una lista de grupos dejando solo los que `user` puede ver."""
    return [group for group in groups if user_can_access_group(group, user)]
