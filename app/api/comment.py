from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.schemas.comment import CommentUpsertRequest, CommentRead
from app.core.services.comment_service import CommentService
from app.core.security import require_authenticated, require_tutor_or_coordinator, require_coordinator


router = APIRouter(tags=["Comments"])
service = CommentService()


@router.get("/api/deliverables/{deliverable_id}/comments", response_model=list[CommentRead], dependencies=[Depends(require_authenticated)])
def list_comments_by_deliverable(deliverable_id: int, db: Session = Depends(get_db)):
    return service.list_comments_by_deliverable(db, deliverable_id)


@router.put(
    "/api/deliverables/{deliverable_id}/comments",
    response_model=CommentRead,
    dependencies=[Depends(require_tutor_or_coordinator)]
)
def upsert_comment(
    deliverable_id: int,
    payload: CommentUpsertRequest,
    db: Session = Depends(get_db),
):
    return service.upsert_comment(db, deliverable_id, payload)


@router.delete("/api/comments/{id}", status_code=204, dependencies=[Depends(require_tutor_or_coordinator)])
def delete_comment(id: int, db: Session = Depends(get_db)):
    service.delete_comment(db, id)