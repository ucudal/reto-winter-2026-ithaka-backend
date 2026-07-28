from fastapi import HTTPException, status
from sqlalchemy.orm import Session
<<<<<<< HEAD
from app.core.models.group import Group
from app.core.repositories.student_repository import StudentRepository
from app.core.schemas.student import StudentUpsert
=======

from app.core.models.group import Group
from app.core.repositories.studentt_repository import StudentRepository
from app.core.schemas.student import StudentListResponse, StudentUpsert
>>>>>>> ddb67f66230fd7766bf4dc7f3a36e58df9fa0537


class StudentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = StudentRepository(db)

    def _check_group_exists(self, group_id: int | None) -> None:
        if group_id is not None and self.db.get(Group, group_id) is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group not found")

<<<<<<< HEAD
    def list_students(self):
        return self.repo.get_all()
=======
    def list_students(
        self,
        group_id: int | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> StudentListResponse:
        items, total_items = self.repo.get_all(
            group_id=group_id, search=search, page=page, page_size=page_size
        )
        return StudentListResponse(
            items=items, total_items=total_items, page=page, page_size=page_size
        )
>>>>>>> ddb67f66230fd7766bf4dc7f3a36e58df9fa0537

    def get_student(self, student_id: int):
        student = self.repo.get_by_id(student_id)
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        return student

    def upsert_student(self, data: StudentUpsert):
        self._check_group_exists(data.group_id)
<<<<<<< HEAD
        
        if data.id is None:
            return self.repo.create(data)
        
=======

        if data.id is None:
            return self.repo.create(data)

>>>>>>> ddb67f66230fd7766bf4dc7f3a36e58df9fa0537
        student = self.repo.get_by_id(data.id)

        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

        return self.repo.update(student, data)

    def delete_student(self, student_id: int):
        student = self.get_student(student_id)  # 404 si no existe
<<<<<<< HEAD
        self.repo.delete(student)
=======
        self.repo.delete(student)
>>>>>>> ddb67f66230fd7766bf4dc7f3a36e58df9fa0537
