from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models.checkpoint import Checkpoint


class CheckpointRepository:


    def list(
        self,
        db: Session
    ):
        statement = select(Checkpoint)

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
    