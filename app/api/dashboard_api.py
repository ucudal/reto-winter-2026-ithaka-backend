from fastapi import APIRouter, Depends

from app.core.schemas.dashboard import DashboardSummary
from app.core.security import require_tutor_or_coordinator
from app.core.services.dashboard_service import DashboardService, get_dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary, dependencies=[Depends(require_tutor_or_coordinator)])
def get_dashboard_summary(service: DashboardService = Depends(get_dashboard_service)):
    return service.get_summary()

