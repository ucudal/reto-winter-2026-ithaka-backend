from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db.session import get_db  # ajustá al import real de tu sesión
from app.core.schemas.stage import ExpectedDeliverableRead, StageRead, StageUpsert
from app.core.services.stage_service import StageService

router = APIRouter(prefix="/api/stages", tags=["stages"])


def get_service(db: Session = Depends(get_db)) -> StageService:
    return StageService(db)


@router.get("", response_model=list[StageRead])
def list_stages(service: StageService = Depends(get_service)):
    return service.get_all()


@router.put("/{stage_id}", response_model=StageRead)
def upsert_stage(
    stage_id: int, data: StageUpsert, service: StageService = Depends(get_service)
):
    return service.upsert(stage_id, data)


@router.get("/{stage_id}/expected-deliverables", response_model=list[ExpectedDeliverableRead])
def get_expected_deliverables(
    stage_id: int, service: StageService = Depends(get_service)
):
    deliverables = service.get_expected_deliverables(stage_id)
    if deliverables is None:
        raise HTTPException(status_code=404, detail="Etapa no encontrada")
    return deliverables