from collections import defaultdict

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.repositories.dashboard_repository import DashboardRepository
from app.core.schemas.dashboard import (
    CapacityInfo,
    DashboardAlert,
    DashboardSummary,
    GroupsByStage,
)


class DashboardService:
    def __init__(self, db: Session):
        self.repository = DashboardRepository(db)

    def get_summary(self) -> DashboardSummary:
        active_groups = self.repository.get_active_groups()
        active_tutors = self.repository.get_active_tutors()
        group_ids = [group.id for group in active_groups]
        meetings = self.repository.get_meetings_by_group_ids(group_ids)

        groups_by_stage = [
            GroupsByStage(stage=stage, count=count)
            for stage, count in self.repository.get_groups_by_stage()
        ]

        return DashboardSummary(
            active_groups=len(active_groups),
            active_tutors=len(active_tutors),
            groups_by_stage=groups_by_stage,
            capacity=self._build_capacity(active_tutors, meetings),
            pending_deliverables=self.repository.get_pending_deliverables_count(),
            alerts=self._build_alerts(active_groups, active_tutors, meetings),
        )

    @staticmethod
    def _build_capacity(active_tutors, meetings) -> CapacityInfo:
        total_available_hours = sum(tutor.max_capacity for tutor in active_tutors)
        total_used_hours = sum(float(meeting.hours_spent or 0) for meeting in meetings)
        usage_percentage = (
            round(total_used_hours / total_available_hours * 100, 1)
            if total_available_hours > 0
            else 0.0
        )
        return CapacityInfo(
            total_available_hours=total_available_hours,
            total_used_hours=total_used_hours,
            usage_percentage=usage_percentage,
        )

    def _build_alerts(self, active_groups, active_tutors, meetings) -> list[DashboardAlert]:
        return (
            self._groups_without_tutor_alerts(active_groups)
            + self._overloaded_tutor_alerts(active_tutors, meetings)
        )

    @staticmethod
    def _groups_without_tutor_alerts(active_groups) -> list[DashboardAlert]:
        alerts = []
        for group in active_groups:
            missing_business = group.business_tutor_id is None
            missing_technical = group.technical_tutor_id is None
            if missing_business and missing_technical:
                description = "Missing business and technical tutor"
            elif missing_business:
                description = "Missing business tutor"
            elif missing_technical:
                description = "Missing technical tutor"
            else:
                continue
            alerts.append(
                DashboardAlert(type="GroupWithoutTutor", group_id=group.id, description=description)
            )
        return alerts

    @staticmethod
    def _overloaded_tutor_alerts(active_tutors, meetings) -> list[DashboardAlert]:
        hours_by_tutor: dict[int, float] = defaultdict(float)
        for meeting in meetings:
            for tutor_id in meeting.tutor_ids or []:
                hours_by_tutor[tutor_id] += float(meeting.hours_spent or 0)

        alerts = []
        for tutor in active_tutors:
            used_hours = hours_by_tutor.get(tutor.id, 0.0)
            if tutor.max_capacity > 0 and used_hours > tutor.max_capacity:
                percentage = round(used_hours / tutor.max_capacity * 100)
                alerts.append(
                    DashboardAlert(
                        type="OverloadedTutor",
                        tutor_id=tutor.id,
                        description=f"{percentage}% of capacity",
                    )
                )
        return alerts


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db)