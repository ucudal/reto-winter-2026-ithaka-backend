import pytest

from datetime import date
from app.core.models.deliverable import Deliverable
from app.core.models.document import Document
from app.core.models.enums import DocumentPlatform, EntityType
from app.core.models.group import Group
from app.core.repositories.document_repository import DocumentRepository
from app.core.schemas.document import DocumentUpsertRequest



@pytest.fixture
def repository():
    return DocumentRepository()


@pytest.fixture(autouse=True)
def _skip_id_sequence_sync(monkeypatch):
    
    monkeypatch.setattr(
        DocumentRepository, "_sync_id_sequence", lambda self, db: None
    )



class TestGetById:

    def test_returns_document_when_exists(self, db_session, repository):
        document = Document(
            entity_type=EntityType.GROUP,
            entity_id=1,
            url="https://drive.google.com/doc-1",
            platform=DocumentPlatform.DRIVE,
            order=1,
        )
        db_session.add(document)
        db_session.commit()

        result = repository.get_by_id(db_session, document.id)

        assert result is not None
        assert result.url == "https://drive.google.com/doc-1"

    def test_returns_none_when_does_not_exist(self, db_session, repository):
        result = repository.get_by_id(db_session, 999)

        assert result is None



class TestListByEntity:

    def test_returns_only_documents_of_that_entity(self, db_session, repository):
        db_session.add_all([
            Document(entity_type=EntityType.GROUP, entity_id=1, url="https://drive.google.com/a", platform=DocumentPlatform.DRIVE, order=1),
            Document(entity_type=EntityType.GROUP, entity_id=1, url="https://drive.google.com/b", platform=DocumentPlatform.DRIVE, order=2),
            Document(entity_type=EntityType.GROUP, entity_id=2, url="https://drive.google.com/c", platform=DocumentPlatform.DRIVE, order=1),
            Document(entity_type=EntityType.DELIVERABLE, entity_id=1, url="https://drive.google.com/d", platform=DocumentPlatform.DRIVE, order=1),
        ])
        db_session.commit()

        result = repository.list_by_entity(db_session, EntityType.GROUP, 1)

        assert len(result) == 2
        assert all(doc.entity_type == EntityType.GROUP and doc.entity_id == 1 for doc in result)

    def test_returns_empty_list_when_no_documents(self, db_session, repository):
        result = repository.list_by_entity(db_session, EntityType.GROUP, 999)

        assert result == []

    def test_returns_documents_ordered_by_order_field(self, db_session, repository):
        db_session.add_all([
            Document(entity_type=EntityType.GROUP, entity_id=1, url="https://drive.google.com/second", platform=DocumentPlatform.DRIVE, order=2),
            Document(entity_type=EntityType.GROUP, entity_id=1, url="https://drive.google.com/first", platform=DocumentPlatform.DRIVE, order=1),
        ])
        db_session.commit()

        result = repository.list_by_entity(db_session, EntityType.GROUP, 1)

        assert result[0].url == "https://drive.google.com/first"
        assert result[1].url == "https://drive.google.com/second"



class TestCreate:

    def test_creates_document_with_correct_entity(self, db_session, repository):
        payload = DocumentUpsertRequest(
            url="https://drive.google.com/new-doc",
            platform=DocumentPlatform.DRIVE,
            order=1,
        )

        result = repository.create(db_session, EntityType.GROUP, 5, payload)

        assert result.id is not None
        assert result.entity_type == EntityType.GROUP
        assert result.entity_id == 5
        assert result.url == "https://drive.google.com/new-doc"

    def test_persists_document_in_database(self, db_session, repository):
        payload = DocumentUpsertRequest(
            url="https://drive.google.com/new-doc",
            platform=DocumentPlatform.DRIVE,
            order=1,
        )

        created = repository.create(db_session, EntityType.GROUP, 5, payload)
        found = repository.get_by_id(db_session, created.id)

        assert found is not None
        assert found.id == created.id



class TestUpdate:

    def test_updates_document_fields(self, db_session, repository):
        document = Document(
            entity_type=EntityType.GROUP,
            entity_id=1,
            url="https://drive.google.com/old",
            platform=DocumentPlatform.DRIVE,
            order=1,
        )
        db_session.add(document)
        db_session.commit()

        payload = DocumentUpsertRequest(
            url="https://drive.google.com/updated",
            platform=DocumentPlatform.SHAREPOINT,
            order=2,
        )
        result = repository.update(db_session, document, payload)

        assert result.url == "https://drive.google.com/updated"
        assert result.platform == DocumentPlatform.SHAREPOINT
        assert result.order == 2

    def test_does_not_change_entity_type_or_id(self, db_session, repository):
        document = Document(
            entity_type=EntityType.GROUP,
            entity_id=1,
            url="https://drive.google.com/old",
            platform=DocumentPlatform.DRIVE,
            order=1,
        )
        db_session.add(document)
        db_session.commit()

        payload = DocumentUpsertRequest(url="https://drive.google.com/updated", platform=DocumentPlatform.DRIVE, order=1)
        result = repository.update(db_session, document, payload)

        assert result.entity_type == EntityType.GROUP
        assert result.entity_id == 1



class TestDelete:

    def test_removes_document_from_database(self, db_session, repository):
        document = Document(
            entity_type=EntityType.GROUP,
            entity_id=1,
            url="https://drive.google.com/to-delete",
            platform=DocumentPlatform.DRIVE,
            order=1,
        )
        db_session.add(document)
        db_session.commit()
        document_id = document.id

        repository.delete(db_session, document)

        assert repository.get_by_id(db_session, document_id) is None



class TestGroupExists:

    def test_returns_true_when_group_exists(self, db_session, repository):
        group = Group(name="Test Group", cohort_id=1, status="Active")
        db_session.add(group)
        db_session.commit()

        assert repository.group_exists(db_session, group.id) is True

    def test_returns_false_when_group_does_not_exist(self, db_session, repository):
        assert repository.group_exists(db_session, 999) is False



class TestDeliverableExists:

    def test_returns_true_when_deliverable_exists(self, db_session, repository):
        deliverable = Deliverable(group_id=1, stage_id=1, expected_date=date(2026, 4, 20), status="Pending")
        db_session.add(deliverable)
        db_session.commit()

        assert repository.deliverable_exists(db_session, deliverable.id) is True

    def test_returns_false_when_deliverable_does_not_exist(self, db_session, repository):
        assert repository.deliverable_exists(db_session, 999) is False