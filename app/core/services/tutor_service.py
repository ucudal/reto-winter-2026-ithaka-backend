from sqlalchemy import false


class TutorService:
    
    def list_tutors(self):
        return [
            {
                "id": 8,
                "name": "María Pérez",
                "role": "Business",
                "specialty": "Strategy and market validation",
                "availability": "Monday and Wednesday afternoon",
                "max_capacity": 88,
                "status": "Active",
            }
        ]

    def get_tutor(self, tutor_id: int):
        return {
            "id": tutor_id,
            "name": "María Pérez",
            "role": "Business",
            "specialty": "Strategy and market validation",
            "availability": "Monday and Wednesday afternoon",
            "max_capacity": 88,
            "status": "Active",
        }
        
        
    def get_tutor_capacity(self, tutor_id: int):
        return {
            "tutor_id": 8,
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