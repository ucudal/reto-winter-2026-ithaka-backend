from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models.comment import Comment


class CommentRepository:

    def list_by_deliverable(self, db: Session, deliverable_id: int) -> list[Comment]:
        statement = select(Comment).where(Comment.deliverable_id == deliverable_id)
        return list(db.scalars(statement).all())