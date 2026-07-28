from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.models.comment import Comment
from app.core.repositories.comment_repository import CommentRepository
from app.core.schemas.comment import CommentUpsertRequest


class CommentService:

    def __init__(self):
        self.repo = CommentRepository()

    def list_comments_by_deliverable(self, db: Session, deliverable_id: int) -> list[Comment]:
        return self.repo.list_by_deliverable(db, deliverable_id)

    def upsert_comment(
        self,
        db: Session,
        deliverable_id: int,
        payload: CommentUpsertRequest,
    ) -> Comment:

        if payload.id is None:
            return self.repo.create(
                db,
                payload.tutor_id,
                deliverable_id,
                payload.content,
            )

        comment = self.repo.get_by_id(db, payload.id)

        if comment is None:
            raise HTTPException(
                status_code=404,
                detail=f"Comment {payload.id} not found",
            )

        return self.repo.update(
            db,
            comment,
            payload.tutor_id,
            payload.content,
        )

    def delete_comment(self, db: Session, comment_id: int) -> None:
        comment = self.repo.get_by_id(db, comment_id)
        if comment is None:
            raise HTTPException(status_code=404, detail=f"Comment {comment_id} not found")
        self.repo.delete(db, comment)