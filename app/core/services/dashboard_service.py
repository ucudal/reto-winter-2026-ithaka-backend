from collections import defaultdict
from datetime import datetime, timezone

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.repositories.dashboard_repository import DashboardRepository
from app.core.schemas.dashboard import (
    CapacityInfo,
    DashboardAlert,
    DashboardSummary,
    GroupHours,
    GroupsByCohort,
    GroupsByStage,
)

# Un grupo sin reuniones en los últimos N días dispara la alerta StaleGroup.
STALE_GROUP_THRESHOLD_DAYS = 14


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
        groups_by_cohort = [
            GroupsByCohort(cohort=f"{year}-S{semester}", count=count)
            for year, semester, count in self.repository.get_groups_by_cohort()
        ]

        hours_by_group_map = self._hours_by_group(meetings)
        hours_by_group = [
            GroupHours(
                group_id=group.id,
                group_name=group.name,
                hours_used=hours_by_group_map.get(group.id, 0.0),
            )
            for group in active_groups
        ]

        return DashboardSummary(
            active_groups=len(active_groups),
            active_tutors=len(active_tutors),
            groups_by_stage=groups_by_stage,
            groups_by_cohort=groups_by_cohort,
            hours_by_group=hours_by_group,
            capacity=self._build_capacity(active_tutors, meetings),
            pending_deliverables=self.repository.get_pending_deliverables_count(),
            alerts=self._build_alerts(active_groups, active_tutors, meetings, group_ids),
        )

    @staticmethod
    def _group_context(group) -> dict:
        return {
            "group_name": group.name,
            "stage_name": group.current_stage.name if group.current_stage else None,
        }

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

    def _build_alerts(self, active_groups, active_tutors, meetings, group_ids) -> list[DashboardAlert]:
        group_by_id = {group.id: group for group in active_groups}
        return (
            self._groups_without_tutor_alerts(active_groups)
            + self._overloaded_tutor_alerts(active_tutors, meetings)
            + self._overdue_deliverable_alerts(group_ids, group_by_id)
            + self._stale_group_alerts(active_groups, meetings)
        )

    @staticmethod
    def _hours_by_group(meetings) -> dict[int, float]:
        hours: dict[int, float] = defaultdict(float)
        for meeting in meetings:
            hours[meeting.group_id] += float(meeting.hours_spent or 0)
        return hours

    def _overdue_deliverable_alerts(self, group_ids, group_by_id) -> list[DashboardAlert]:
        overdue = self.repository.get_overdue_deliverables(group_ids)
        alerts = []
        for deliverable in overdue:
            group = group_by_id.get(deliverable.group_id)
            context = self._group_context(group) if group else {}
            alerts.append(
                DashboardAlert(
                    type="OverdueDeliverable",
                    group_id=deliverable.group_id,
                    description=f"Entregable vencido desde {deliverable.expected_date.isoformat()}",
                    **context,
                )
            )
        return alerts

    def _stale_group_alerts(self, active_groups, meetings) -> list[DashboardAlert]:
        last_meeting_by_group: dict[int, datetime] = {}
        for meeting in meetings:
            current = last_meeting_by_group.get(meeting.group_id)
            if current is None or meeting.date > current:
                last_meeting_by_group[meeting.group_id] = meeting.date

        now = datetime.now(timezone.utc)
        alerts = []
        for group in active_groups:
            last_meeting = last_meeting_by_group.get(group.id)
            if last_meeting is None:
                alerts.append(
                    DashboardAlert(
                        type="StaleGroup",
                        group_id=group.id,
                        description="Sin reuniones registradas",
                        **self._group_context(group),
                    )
                )
                continue

            days_since = (now - last_meeting).days
            if days_since > STALE_GROUP_THRESHOLD_DAYS:
                alerts.append(
                    DashboardAlert(
                        type="StaleGroup",
                        group_id=group.id,
                        description=f"Sin reuniones hace {days_since} días",
                        **self._group_context(group),
                    )
                )
        return alerts

    def _groups_without_tutor_alerts(self, active_groups) -> list[DashboardAlert]:
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
                DashboardAlert(
                    type="GroupWithoutTutor",
                    group_id=group.id,
                    description=description,
                    **self._group_context(group),
                )
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
                        tutor_name=tutor.name,
                        description=f"{percentage}% of capacity",
                    )
                )
        return alerts


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db)