from fastapi import APIRouter
from sqlalchemy import false

router = APIRouter(
    tags=["Tutors"],
)

@router.get("/api/tutors")
def Tutors():
    return {"id": 8,
            "name": "María Pérez",
            "role": "Business",
            "specialty": "Strategy and market validation",
            "availability": "Monday and Wednesday afternoon",
            "max_capacity": 88,
            "status": "Active"}
    

@router.get("/api/tutors/{id}")
def TutorsId(id: int):
    return {"id": id,
            "name": "María Pérez",
            "role": "Business",
            "specialty": "Strategy and market validation",
            "availability": "Monday and Wednesday afternoon",
            "max_capacity": 88,
            "status": "Active"}
    

@router.get("/api/tutors/{id}/capacity")
def TutorsIdCapacity(id: int):
    return {
            "tutor_id": id,
            "max_capacity": 88,
            "assigned_hours": 66,
            "available_hours": 22,
            "usage_percentage": 75,
            "overloaded": false,
            "groups": [
                { "group_id": 45, "name": "EcoRoute", "hours_consumed": 18 },
                { "group_id": 52, "name": "AgroSmart", "hours_consumed": 22 }
            ]
}


