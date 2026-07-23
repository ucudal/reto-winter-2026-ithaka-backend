from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.schemas.comment import CommentRead
from app.core.services.comment_service import CommentService

router = APIRouter(tags=["Comments"])
service = CommentService()


@router.get("/api/deliverables/{deliverable_id}/comments", response_model=list[CommentRead])
def list_comments_by_deliverable(deliverable_id: int, db: Session = Depends(get_db)):
    return service.list_comments_by_deliverable(db, deliverable_id)


