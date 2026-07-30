from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.core.models.document import Document
from app.core.models.enums import DocumentPlatform, EntityType
from app.core.schemas.document import DocumentUpsertRequest
from app.core.services.document_service import DocumentService



@pytest.fixture
def mock_repository():
    return MagicMock()

@pytest.fixture
def service(mock_repository):
    return DocumentService(repository=mock_repository)

@pytest.fixture
def sample_document():
    return Document(
        id=1,
        entity_type=EntityType.GROUP,
        entity_id=5,
        url="https://drive.google.com/doc-1",
        platform=DocumentPlatform.DRIVE,
        order=1,
    )






class TestListGroupDocuments:

    def test_returns_documents_when_group_exists(self, service, mock_repository, sample_document):
        mock_repository.group_exists.return_value = True
        mock_repository.list_by_entity.return_value = [sample_document]

        result = service.list_group_documents(db=MagicMock(), group_id=5)

        assert len(result) == 1
        assert result[0].url == "https://drive.google.com/doc-1"
        mock_repository.list_by_entity.assert_called_once_with(
            mock_repository.list_by_entity.call_args[0][0], EntityType.GROUP, 5
        )

    def test_raises_404_when_group_does_not_exist(self, service, mock_repository):
        mock_repository.group_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            service.list_group_documents(db=MagicMock(), group_id=999)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Group not found"
        mock_repository.list_by_entity.assert_not_called()




class TestListDeliverableDocuments:

    def test_returns_documents_when_deliverable_exists(self, service, mock_repository, sample_document):
        mock_repository.deliverable_exists.return_value = True
        mock_repository.list_by_entity.return_value = [sample_document]

        result = service.list_deliverable_documents(db=MagicMock(), deliverable_id=3)

        assert len(result) == 1

    def test_raises_404_when_deliverable_does_not_exist(self, service, mock_repository):
        mock_repository.deliverable_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            service.list_deliverable_documents(db=MagicMock(), deliverable_id=999)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Deliverable not found"




class TestUpsertGroupDocumentCreate:

    def test_creates_document_when_no_id_provided(self, service, mock_repository, sample_document):
        mock_repository.group_exists.return_value = True
        mock_repository.create.return_value = sample_document
        payload = DocumentUpsertRequest(url="https://drive.google.com/doc-1", platform=DocumentPlatform.DRIVE, order=1)

        result = service.upsert_group_document(db=MagicMock(), group_id=5, payload=payload)

        assert result.id == 1
        mock_repository.create.assert_called_once()
        mock_repository.update.assert_not_called()

    def test_raises_404_when_group_does_not_exist_on_create(self, service, mock_repository):
        mock_repository.group_exists.return_value = False
        payload = DocumentUpsertRequest(url="https://drive.google.com/doc-1", platform=DocumentPlatform.DRIVE, order=1)

        with pytest.raises(HTTPException) as exc_info:
            service.upsert_group_document(db=MagicMock(), group_id=999, payload=payload)

        assert exc_info.value.status_code == 404




class TestUpsertGroupDocumentUpdate:

    def test_updates_document_when_id_provided_and_belongs_to_entity(
        self, service, mock_repository, sample_document
    ):
        mock_repository.group_exists.return_value = True
        mock_repository.get_by_id.return_value = sample_document
        mock_repository.update.return_value = sample_document
        payload = DocumentUpsertRequest(id=1, url="https://drive.google.com/doc-1-updated", platform=DocumentPlatform.DRIVE, order=2)

        result = service.upsert_group_document(db=MagicMock(), group_id=5, payload=payload)

        assert result.id == 1
        mock_repository.update.assert_called_once()
        mock_repository.create.assert_not_called()

    def test_raises_404_when_document_id_does_not_exist(self, service, mock_repository):
        mock_repository.group_exists.return_value = True
        mock_repository.get_by_id.return_value = None
        payload = DocumentUpsertRequest(id=999, url="https://drive.google.com/doc-1", platform=DocumentPlatform.DRIVE, order=1)

        with pytest.raises(HTTPException) as exc_info:
            service.upsert_group_document(db=MagicMock(), group_id=5, payload=payload)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Document not found"

    def test_raises_400_when_document_belongs_to_different_entity(
        self, service, mock_repository, sample_document
    ):
       
        mock_repository.group_exists.return_value = True
        mock_repository.get_by_id.return_value = sample_document
        payload = DocumentUpsertRequest(id=1, url="https://drive.google.com/doc-1", platform=DocumentPlatform.DRIVE, order=1)

        with pytest.raises(HTTPException) as exc_info:
            service.upsert_group_document(db=MagicMock(), group_id=99, payload=payload)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Document does not belong to this entity"
        mock_repository.update.assert_not_called()



class TestDeleteDocument:

    def test_deletes_document_when_exists(self, service, mock_repository, sample_document):
        mock_repository.get_by_id.return_value = sample_document

        service.delete_document(db=MagicMock(), document_id=1)

        mock_repository.delete.assert_called_once()

    def test_raises_404_when_document_does_not_exist(self, service, mock_repository):
        mock_repository.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            service.delete_document(db=MagicMock(), document_id=999)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Document not found"
        mock_repository.delete.assert_not_called()


