from sqlalchemy.orm import Session
from app.core.models.student import Student
from app.core.schemas.student import StudentUpsert


class StudentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Student]:
        return self.db.query(Student).all()

    def get_by_id(self, student_id: int) -> Student | None:
        return self.db.get(Student, student_id)
    
    def create(self, data: StudentUpsert) -> Student:
        student = Student(
            **data.model_dump(exclude={"id"})
        )

        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)

        return student

    def update(self, student: Student, data: StudentUpsert) -> Student:
        for key, value in data.model_dump(exclude={"id"}).items():
            setattr(student, key, value)
        self.db.commit()
        self.db.refresh(student)
        return student

    def delete(self, student: Student) -> None:
        self.db.delete(student)
        self.db.commit()
        