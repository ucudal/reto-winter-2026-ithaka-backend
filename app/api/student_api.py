@router.get("", response_model=StudentListResponse)
def list_students(
    group_id: int | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return StudentService(db).list_students(
        group_id=group_id, search=search, page=page, page_size=page_size
    )