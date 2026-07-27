from __future__ import annotations

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.models.deliverable import Deliverable
from app.core.models.document import Document
from app.core.models.enums import EntityType
from app.core.models.group import Group
from app.core.schemas.document import DocumentUpsertRequest


class DocumentRepository:

    def get_by_id(self, db: Session, document_id: int) -> Document | None:
        return db.get(Document, document_id)

    def list_by_entity(
        self, db: Session, entity_type: EntityType, entity_id: int
    ) -> list[Document]:
        statement = (
            select(Document)
            .where(
                Document.entity_type == entity_type,
                Document.entity_id == entity_id,
            )
            .order_by(Document.order.asc(), Document.id.asc())
        )
        return list(db.scalars(statement).all())

    def create(
        self,
        db: Session,
        entity_type: EntityType,
        entity_id: int,
        payload: DocumentUpsertRequest,
    ) -> Document:
        document = Document(
            entity_type=entity_type,
            entity_id=entity_id,
            **payload.model_dump(exclude={"id"}),
        )
        db.add(document)
        db.flush()
        self._sync_id_sequence(db)
        db.commit()
        db.refresh(document)
        return document

    def update(
        self, db: Session, document: Document, payload: DocumentUpsertRequest
    ) -> Document:
        for field, value in payload.model_dump(exclude={"id"}).items():
            setattr(document, field, value)

        db.commit()
        db.refresh(document)
        return document

    def delete(self, db: Session, document: Document) -> None:
        db.delete(document)
        db.commit()

    def group_exists(self, db: Session, group_id: int) -> bool:
        return db.get(Group, group_id) is not None

    def deliverable_exists(self, db: Session, deliverable_id: int) -> bool:
        return db.get(Deliverable, deliverable_id) is not None

    def _sync_id_sequence(self, db: Session) -> None:
        sequence_name = db.scalar(text("SELECT pg_get_serial_sequence('documents', 'id')"))
        if sequence_name is None:
            return

        db.execute(
            text("SELECT setval(:sequence_name, COALESCE((SELECT MAX(id) FROM documents), 1), true)"),
            {"sequence_name": sequence_name},
        )