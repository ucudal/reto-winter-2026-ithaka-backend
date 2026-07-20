from enum import Enum


class TutorRole(str, Enum):
    BUSINESS = "Business"
    TECHNICAL = "Technical"


class TutoringType(str, Enum):
    BUSINESS = "Business"
    TECHNICAL = "Technical"


class UserRole(str, Enum):
    COORDINATOR = "Coordinator"
    BUSINESS_TUTOR = "BusinessTutor"
    TECHNICAL_TUTOR = "TechnicalTutor"
    STUDENT = "Student"


class DocumentPlatform(str, Enum):
    DRIVE = "Drive"
    SHAREPOINT = "SharePoint"
