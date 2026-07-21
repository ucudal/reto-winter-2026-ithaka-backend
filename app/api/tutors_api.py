from fastapi import APIRouter
from app.core.services.tutor_service import TutorService

router = APIRouter(tags=["Tutors"])

service = TutorService()

@router.get("/api/tutors")
def list_tutors():
    return service.list_tutors()

@router.get("/api/tutors/{id}")
def get_tutor(id: int):
    return service.get_tutor(id)

@router.get("/api/tutors/{id}/capacity")
def get_tutor_capacity(id: int):
    return service.get_tutor_capacity(id)



