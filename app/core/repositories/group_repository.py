from app.core.models.group import Group

# --- Datos mockeados temporales (hasta que el equipo de BD suba el repository real) ---
groups_db: list[Group] = [
    Group(
        id=1,
        name="Grupo A",
        cohort_id=1,
        current_stage_id=1,
        idea="App para gestión de turnos",
        major="Ingeniería de Sistemas",
        status="Active",
        business_tutor_id=5,
        technical_tutor_id=None,
    ),
    Group(
        id=2,
        name="Grupo B",
        cohort_id=1,
        current_stage_id=2,
        idea="Plataforma de reciclaje",
        major="Ingeniería de Sistemas",
        status="Active",
        business_tutor_id=6,
        technical_tutor_id=8,
    ),
]


def get_all() -> list[Group]:
    return groups_db


def get_by_id(group_id: int) -> Group | None:
    for group in groups_db:
        if group.id == group_id:
            return group
    return None


def create(data) -> Group:
    existing_ids = [g.id for g in groups_db]
    new_id = max(existing_ids, default=0) + 1
    new_group = Group(
        id=new_id,
        name=data.name,
        cohort_id=data.cohort_id,
        current_stage_id=data.current_stage_id,
        idea=data.idea,
        major=data.major,
        business_tutor_id=data.business_tutor_id,
        technical_tutor_id=data.technical_tutor_id,
    )
    groups_db.append(new_group)
    return new_group


def update(group_id: int, data) -> Group | None:
    existing = get_by_id(group_id)
    if existing is None:
        return None
    existing.name = data.name
    existing.cohort_id = data.cohort_id
    existing.current_stage_id = data.current_stage_id
    existing.idea = data.idea
    existing.major = data.major
    existing.status = data.status
    existing.business_tutor_id = data.business_tutor_id
    existing.technical_tutor_id = data.technical_tutor_id
    return existing


def delete(group_id: int) -> bool:
    group = get_by_id(group_id)
    if group is None:
        return False
    groups_db.remove(group)
    return True