from datetime import date, timedelta

from fastapi import HTTPException,status
from sqlalchemy.orm import Session

from app.core.repositories.checkpoint_repository import CheckpointRepository
from app.core.schemas.checkpoint import CheckpointRead



class CheckpointService:


    def __init__(
        self,
        repository=None
    ):
        self.repository = (
            repository or CheckpointRepository()
        )


    def list_checkpoints(
        self,
        db:Session
    ):

        return [
            CheckpointRead.model_validate(
                c,
                from_attributes=True
            )
            for c in self.repository.list(db)
        ]



    def get_checkpoint(
        self,
        db,
        checkpoint_id
    ):

        checkpoint = self.repository.get_by_id(
            db,
            checkpoint_id
        )

        if not checkpoint:
            raise HTTPException(
                404,
                "Checkpoint not found"
            )

        return CheckpointRead.model_validate(
            checkpoint,
            from_attributes=True
        )



    def update_checkpoint(
        self,
        db,
        checkpoint_id,
        payload
    ):

        checkpoint = self.repository.get_by_id(
            db,
            checkpoint_id
        )

        if not checkpoint:
            raise HTTPException(
                404,
                "Checkpoint not found"
            )


        return self.repository.update(
            db,
            checkpoint,
            payload.model_dump()
        )



    def my_pending(
        self,
        db,
        user
    ):

        checkpoints = self.repository.list(db)

        today = date.today()

        result=[]

        for checkpoint in checkpoints:

            reminder_date = (
                checkpoint.due_date
                - timedelta(days=10)
            )

            if today >= reminder_date:

                result.append(checkpoint)


        return result
    