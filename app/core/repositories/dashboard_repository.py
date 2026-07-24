from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.models.deliverable import Deliverable
from app.core.models.group import Group
from app.core.models.meeting import Meeting
from app.core.models.stage import Stage
from app.core.models.tutor import Tutor


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_groups(self) -> list[Group]:
        return self.db.query(Group).filter(Group.status == "Active").all()

    def get_active_tutors(self) -> list[Tutor]:
        return self.db.query(Tutor).filter(Tutor.status == "Active").all()

    def get_groups_by_stage(self) -> list[tuple[str, int]]:
        return (
            self.db.query(Stage.name, func.count(Group.id))
            .join(Group, Group.current_stage_id == Stage.id)
            .filter(Group.status == "Active")
            .group_by(Stage.id, Stage.name)
            .order_by(Stage.order)
            .all()
        )

    def get_pending_deliverables_count(self) -> int:
        return (
            self.db.query(Deliverable)
            .filter(Deliverable.status == "Pending")
            .count()
        )

    def get_meetings_by_group_ids(self, group_ids: list[int]) -> list[Meeting]:
        if not group_ids:
            return []
        return self.db.query(Meeting).filter(Meeting.group_id.in_(group_ids)).all()