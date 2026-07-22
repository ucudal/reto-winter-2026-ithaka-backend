# Si se agrega un modelo hay que agregarlo acá

from app.core.db.base import Base
from app.core.models.cohort import Cohort
from app.core.models.comment import Comment
from app.core.models.deliverable import Deliverable
from app.core.models.document import Document
from app.core.models.group import Group
from app.core.models.meeting import Meeting
from app.core.models.stage import Stage
from app.core.models.student import Student
from app.core.models.support_material import SupportMaterial
from app.core.models.tutor import Tutor
from app.core.models.user import User

__all__ = [
    "Base",
    "Cohort",
    "Comment",
    "Deliverable",
    "Document",
    "Group",
    "Meeting",
    "Stage",
    "Student",
    "SupportMaterial",
    "Tutor",
    "User",
]
