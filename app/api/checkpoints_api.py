from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db.session import get_db
from app.core.models.user import User
from app.core.schemas.checkpoint import (
    CheckpointPendingRead,
    CheckpointRead,
    CheckpointResponseRead,
    CheckpointUpdateRequest,
)
from app.core.security import get_current_user
from app.core.services.checkpoint_service import CheckpointService

router = APIRouter(prefix="/api/checkpoints", tags=["Checkpoints"])


@router.get("", response_model=list[CheckpointRead])
def list_checkpoints(group_id: int | None = None, status: str | None = None, db: Session = Depends(get_db)):
    return CheckpointService().list_checkpoints(db, group_id=group_id, status_filter=status)


@router.get("/my-pending", response_model=list[CheckpointPendingRead])
def my_pending(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return CheckpointService().list_my_pending(db, current_user)


@router.get("/{checkpoint_id}", response_model=CheckpointRead)
def get_checkpoint(checkpoint_id: int, db: Session = Depends(get_db)):
    return CheckpointService().get_checkpoint(db, checkpoint_id)


@router.get("/{checkpoint_id}/responses", response_model=list[CheckpointResponseRead])
def list_responses(checkpoint_id: int, db: Session = Depends(get_db)):
    return CheckpointService().list_responses(db, checkpoint_id)


@router.put("/{checkpoint_id}", response_model=CheckpointRead | None)
def update_checkpoint(checkpoint_id: int, payload: CheckpointUpdateRequest, db: Session = Depends(get_db)):
    return CheckpointService().update_checkpoint(db, checkpoint_id, payload)