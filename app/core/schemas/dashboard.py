from pydantic import BaseModel


class GroupsByStage(BaseModel):
    stage: str
    count: int


class GroupsByCohort(BaseModel):
    cohort: str
    count: int


class GroupHours(BaseModel):
    group_id: int
    group_name: str
    hours_used: float


class CapacityInfo(BaseModel):
    total_available_hours: float
    total_used_hours: float
    usage_percentage: float


class DashboardAlert(BaseModel):
    type: str
    group_id: int | None = None
    group_name: str | None = None
    stage_name: str | None = None
    tutor_id: int | None = None
    tutor_name: str | None = None
    description: str


class DashboardSummary(BaseModel):
    active_groups: int
    active_tutors: int
    groups_by_stage: list[GroupsByStage]
    groups_by_cohort: list[GroupsByCohort]
    hours_by_group: list[GroupHours]
    capacity: CapacityInfo
    pending_deliverables: int
    alerts: list[DashboardAlert]