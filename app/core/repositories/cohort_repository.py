from __future__ import annotations

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.models.cohort import Cohort
from app.core.models.group import Group
from app.core.models.stage import Stage
from app.core.schemas.cohort import CohortUpsertRequest


class CohortRepository:

    def list(self, db: Session) -> list[Cohort]:
        statement = select(Cohort).order_by(
            Cohort.year.desc(), Cohort.semester.desc(), Cohort.id.desc()
        )
        return list(db.scalars(statement).all())

    def get_by_id(self, db: Session, cohort_id: int) -> Cohort | None:
        return db.get(Cohort, cohort_id)

    def upsert(self, db: Session, cohort_id: int, payload: CohortUpsertRequest) -> Cohort:
        cohort = self.get_by_id(db, cohort_id)
        if cohort is None:
            cohort = Cohort(id=cohort_id, **payload.model_dump())
            db.add(cohort)
            db.flush()
            self._sync_id_sequence(db)
        else:
            for field, value in payload.model_dump().items():
                setattr(cohort, field, value)

        db.commit()
        db.refresh(cohort)
        return cohort

    def count_groups(self, db: Session, cohort_id: int) -> int:
        statement = select(func.count()).select_from(Group).where(Group.cohort_id == cohort_id)
        return db.scalar(statement) or 0

    def list_groups(self, db: Session, cohort_id: int) -> list[Group]:
        statement = select(Group).where(Group.cohort_id == cohort_id).order_by(
            Group.name.asc(), Group.id.asc()
        )
        return list(db.scalars(statement).all())

    def list_stages(self, db: Session, cohort_id: int) -> list[Stage]:
        statement = select(Stage).where(Stage.cohort_id == cohort_id).order_by(
            Stage.order.asc(), Stage.id.asc()
        )
        return list(db.scalars(statement).all())

    def _sync_id_sequence(self, db: Session) -> None:
        sequence_name = db.scalar(text("SELECT pg_get_serial_sequence('cohorts', 'id')"))
        if sequence_name is None:
            return

        db.execute(
            text("SELECT setval(:sequence_name, COALESCE((SELECT MAX(id) FROM cohorts), 1), true)"),
            {"sequence_name": sequence_name},
        )
