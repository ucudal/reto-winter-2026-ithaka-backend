from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.db.session import get_db
from app.core.schemas.student import StudentUpsert, StudentRead
from app.core.services.student_service import StudentService

router = APIRouter(prefix="/api/students", tags=["Students"])


@router.get("", response_model=list[StudentRead])
def list_students(db: Session = Depends(get_db)):
    return StudentService(db).list_students()


@router.get("/{student_id}", response_model=StudentRead)
def get_student(student_id: int, db: Session = Depends(get_db)):
    return StudentService(db).get_student(student_id)


@router.put("", response_model=StudentRead)
def upsert_student(data: StudentUpsert, db: Session = Depends(get_db)):
    return StudentService(db).upsert_student(data)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    StudentService(db).delete_student(student_id)
