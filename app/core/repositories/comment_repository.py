from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models.comment import Comment


class CommentRepository:

    def list_by_deliverable(self, db: Session, deliverable_id: int) -> list[Comment]:
        statement = select(Comment).where(Comment.deliverable_id == deliverable_id)
        return list(db.scalars(statement).all())

    def get_by_id(self, db: Session, comment_id: int) -> Comment | None:
        return db.get(Comment, comment_id)

    def create(self, db: Session, tutor_id: int, deliverable_id: int, content: str) -> Comment:
        comment = Comment(tutor_id=tutor_id, deliverable_id=deliverable_id, content=content)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment

    def delete(self, db: Session, comment: Comment) -> None:
        db.delete(comment)
        db.commit()