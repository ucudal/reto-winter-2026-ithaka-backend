from fastapi import APIRouter, Depends

from app.core.schemas.dashboard import DashboardSummary
from app.core.services.dashboard_service import DashboardService, get_dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(service: DashboardService = Depends(get_dashboard_service)):
    return service.get_summary()

