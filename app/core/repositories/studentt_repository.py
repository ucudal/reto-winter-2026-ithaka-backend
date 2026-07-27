def get_all(
    self,
    group_id: int | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Student], int]:
    query = self.db.query(Student)

    # TODO: si group_id no es None, filtrar query por Student.group_id == group_id
    # TODO: si search no es None, filtrar por Student.name (o email) usando ILIKE
    #       (case-insensitive), algo como Student.name.ilike(f"%{search}%")

    total_items = query.count()  # ojo: contar ANTES de aplicar offset/limit

    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    return items, total_items