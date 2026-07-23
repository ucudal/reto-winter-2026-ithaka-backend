from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.schemas.document import DocumentRead, DocumentUpsertRequest
from app.core.services.document_service import DocumentService

router = APIRouter(
    prefix="/api",
    tags=["Documents"],
)


def get_document_service() -> DocumentService:
    return DocumentService()


@router.get("/groups/{group_id}/documents", response_model=list[DocumentRead])
def list_group_documents(
    group_id: int,
    db: Session = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
):
    return service.list_group_documents(db, group_id)


@router.put("/groups/{group_id}/documents", response_model=DocumentRead)
def upsert_group_document(
    group_id: int,
    payload: DocumentUpsertRequest,
    db: Session = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
):
    return service.upsert_group_document(db, group_id, payload)


@router.get("/deliverables/{deliverable_id}/documents", response_model=list[DocumentRead])
def list_deliverable_documents(
    deliverable_id: int,
    db: Session = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
):
    return service.list_deliverable_documents(db, deliverable_id)


@router.put("/deliverables/{deliverable_id}/documents", response_model=DocumentRead)
def upsert_deliverable_document(
    deliverable_id: int,
    payload: DocumentUpsertRequest,
    db: Session = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
):
    return service.upsert_deliverable_document(db, deliverable_id, payload)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
):
    service.delete_document(db, document_id)