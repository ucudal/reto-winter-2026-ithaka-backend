from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.core.models.checkpoint import Checkpoint
from app.core.models.group import Group


class CheckpointRepository:


    def list(
        self,
        db: Session,
        group_id: int | None = None,
        search: str | None = None,
    ):

        statement = (
            select(Checkpoint)
            .join(Group)
        )

        if group_id is not None:
            statement = statement.where(
                Checkpoint.group_id == group_id
            )

        if search:
            statement = statement.where(
                Group.name.ilike(f"%{search}%")
            )

        return list(
            db.scalars(statement).all()
        )


    def get_by_id(
        self,
        db: Session,
        checkpoint_id: int
    ):
        return db.get(
            Checkpoint,
            checkpoint_id
        )


    def update(
        self,
        db: Session,
        checkpoint,
        data
    ):

        for field,value in data.items():
            if value is not None:
                setattr(
                    checkpoint,
                    field,
                    value
                )

        db.commit()
        db.refresh(checkpoint)

        return checkpoint
    