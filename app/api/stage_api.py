from fastapi import APIRouter, Depends, HTTPException

from app.core.schemas.stage import ExpectedDeliverableRead, StageRead, StageUpsert
from app.core.services.stage_service import StageService, get_stage_service

router = APIRouter(prefix="/api/stages", tags=["stages"])


@router.get("", response_model=list[StageRead])
def list_stages(service: StageService = Depends(get_stage_service)):
    return service.get_all()


@router.put("/{stage_id}", response_model=StageRead)
def upsert_stage(stage_id: int, data: StageUpsert, service: StageService = Depends(get_stage_service)):
    return service.upsert(stage_id, data)


@router.get("/{stage_id}/expected-deliverables", response_model=list[ExpectedDeliverableRead])
def get_expected_deliverables(stage_id: int, service: StageService = Depends(get_stage_service)):
    deliverables = service.get_expected_deliverables(stage_id)
    return service.get_expected_deliverables(stage_id)