from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.models.user import User
from app.core.security import (
    get_current_user,
    require_authenticated
)

from app.core.services.checkpoint_service import CheckpointService
from app.core.schemas.checkpoint import (
    CheckpointRead,
    CheckpointUpdateRequest
)


router = APIRouter(
    prefix="/api/checkpoints",
    tags=["Checkpoints"]
)



def get_checkpoint_service():
    return CheckpointService()



@router.get(
    "",
    response_model=list[CheckpointRead],
    dependencies=[Depends(require_authenticated)]
)
def list_checkpoints(
    group_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    service: CheckpointService = Depends(get_checkpoint_service)
):
    return service.list_checkpoints(
        db=db,
        group_id=group_id,
        search=search
    )


@router.get(
    "/my-pending",
    response_model=list[CheckpointRead]
)
def my_pending(
    current_user:User=Depends(get_current_user),
    db:Session=Depends(get_db),
    service:CheckpointService=Depends(get_checkpoint_service)
):

    return service.my_pending(
        db,
        current_user
    )



@router.get(
    "/{id}",
    response_model=CheckpointRead
)
def get_checkpoint(
    id:int,
    db:Session=Depends(get_db),
    service:CheckpointService=Depends(get_checkpoint_service)
):

    return service.get_checkpoint(
        db,
        id
    )



@router.put(
    "/{id}",
    response_model=CheckpointRead
)
def update_checkpoint(
    id:int,
    payload:CheckpointUpdateRequest,
    db:Session=Depends(get_db),
    service:CheckpointService=Depends(get_checkpoint_service)
):

    return service.update_checkpoint(
        db,
        id,
        payload
    )
