from pydantic import BaseModel


class GroupsByStage(BaseModel):
    stage: str
    count: int


class CapacityInfo(BaseModel):
    total_available_hours: float
    total_used_hours: float
    usage_percentage: float


class DashboardAlert(BaseModel):
    type: str
    group_id: int | None = None
    tutor_id: int | None = None
    description: str


class DashboardSummary(BaseModel):
    active_groups: int
    active_tutors: int
    groups_by_stage: list[GroupsByStage]
    capacity: CapacityInfo
    pending_deliverables: int
    alerts: list[DashboardAlert]