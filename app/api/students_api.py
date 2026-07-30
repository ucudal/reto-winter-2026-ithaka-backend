from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.db.session import get_db
from app.core.schemas.student import StudentUpsert, StudentRead
from app.core.security import require_authenticated, require_coordinator, require_tutor_or_coordinator
from app.core.services.student_service import StudentService

router = APIRouter(prefix="/api/students", tags=["Students"])


from app.core.schemas.pagination import PaginatedResponse


@router.get("", response_model=PaginatedResponse[StudentRead], dependencies=[Depends(require_tutor_or_coordinator)])
def list_students(
    group_id: int | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = StudentService(db).list_students(
        group_id=group_id,
        search=search,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{student_id}", response_model=StudentRead, dependencies=[Depends(require_authenticated)])
def get_student(student_id: int, db: Session = Depends(get_db)):
    return StudentService(db).get_student(student_id)


@router.put("", response_model=StudentRead, dependencies=[Depends(require_coordinator)])
def upsert_student(data: StudentUpsert, db: Session = Depends(get_db)):
    return StudentService(db).upsert_student(data)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_coordinator)])
def delete_student(student_id: int, db: Session = Depends(get_db)):
    StudentService(db).delete_student(student_id)
