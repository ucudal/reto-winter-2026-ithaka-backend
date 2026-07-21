from fastapi import APIRouter
from app.core.services.tutor_service import TutorService

router = APIRouter(tags=["Tutors"])


@router.get("/api/tutors")
def list_tutors():
    service = TutorService()
    return service.list_tutors()


@router.get("/api/tutors/{id}")
def get_tutor(id: int):
    service = TutorService()
    return service.get_tutor(id)

@router.get("/api/tutors/{id}/capacity")
def get_tutor_capacity(id: int):
    service = TutorService()
    return service.get_tutor_capacity(id)



