from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.models.enums import EntityType
from app.core.repositories.document_repository import DocumentRepository
from app.core.schemas.document import DocumentRead, DocumentUpsertRequest


class DocumentService:

    def __init__(self, repository: DocumentRepository | None = None):
        self.repository = repository or DocumentRepository()

    def list_group_documents(self, db: Session, group_id: int) -> list[DocumentRead]:
        self._ensure_group(db, group_id)
        return self._list(db, EntityType.GROUP, group_id)

    def list_deliverable_documents(
        self, db: Session, deliverable_id: int
    ) -> list[DocumentRead]:
        self._ensure_deliverable(db, deliverable_id)
        return self._list(db, EntityType.DELIVERABLE, deliverable_id)

    def upsert_group_document(
        self, db: Session, group_id: int, payload: DocumentUpsertRequest
    ) -> DocumentRead:
        self._ensure_group(db, group_id)
        return self._upsert(db, EntityType.GROUP, group_id, payload)

    def upsert_deliverable_document(
        self, db: Session, deliverable_id: int, payload: DocumentUpsertRequest
    ) -> DocumentRead:
        self._ensure_deliverable(db, deliverable_id)
        return self._upsert(db, EntityType.DELIVERABLE, deliverable_id, payload)

    def delete_document(self, db: Session, document_id: int) -> None:
        document = self._get_or_404(db, document_id)
        self.repository.delete(db, document)

    def _list(
        self, db: Session, entity_type: EntityType, entity_id: int
    ) -> list[DocumentRead]:
        documents = self.repository.list_by_entity(db, entity_type, entity_id)
        return [
            DocumentRead.model_validate(document, from_attributes=True)
            for document in documents
        ]

    def _upsert(
        self,
        db: Session,
        entity_type: EntityType,
        entity_id: int,
        payload: DocumentUpsertRequest,
    ) -> DocumentRead:
        if payload.id is None:
            document = self.repository.create(db, entity_type, entity_id, payload)
        else:
            document = self._get_or_404(db, payload.id)
            if document.entity_type != entity_type or document.entity_id != entity_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Document does not belong to this entity",
                )
            document = self.repository.update(db, document, payload)

        return DocumentRead.model_validate(document, from_attributes=True)

    def _get_or_404(self, db: Session, document_id: int):
        document = self.repository.get_by_id(db, document_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        return document

    def _ensure_group(self, db: Session, group_id: int) -> None:
        if not self.repository.group_exists(db, group_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found",
            )

    def _ensure_deliverable(self, db: Session, deliverable_id: int) -> None:
        if not self.repository.deliverable_exists(db, deliverable_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deliverable not found",
            )