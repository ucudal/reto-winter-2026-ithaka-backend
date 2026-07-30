from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.core.models.comment import Comment
from app.core.schemas.comment import CommentUpsertRequest
from app.core.services.comment_service import CommentService


@pytest.fixture
def mock_repository():
    return MagicMock()


@pytest.fixture
def service(mock_repository):
    svc = CommentService()
    svc.repo = mock_repository  
    return svc


@pytest.fixture
def sample_comment():
    return Comment(
        id=1,
        tutor_id=8,
        deliverable_id=5,
        content="Needs deeper competitive analysis",
    )



class TestListCommentsByDeliverable:

    def test_returns_comments_of_deliverable(self, service, mock_repository, sample_comment):
        mock_repository.list_by_deliverable.return_value = [sample_comment]

        result = service.list_comments_by_deliverable(db=MagicMock(), deliverable_id=5)

        assert len(result) == 1
        assert result[0].content == "Needs deeper competitive analysis"

    def test_returns_empty_list_when_no_comments(self, service, mock_repository):
        mock_repository.list_by_deliverable.return_value = []

        result = service.list_comments_by_deliverable(db=MagicMock(), deliverable_id=999)

        assert result == []




class TestUpsertCommentCreate:

    def test_creates_comment_when_no_id_provided(self, service, mock_repository, sample_comment):
        mock_repository.create.return_value = sample_comment
        payload = CommentUpsertRequest(tutor_id=8, content="Needs deeper competitive analysis")

        result = service.upsert_comment(db=MagicMock(), deliverable_id=5, payload=payload)

        assert result.id == 1
        mock_repository.create.assert_called_once()
        mock_repository.update.assert_not_called()

    def test_create_passes_correct_arguments(self, service, mock_repository, sample_comment):
        mock_repository.create.return_value = sample_comment
        payload = CommentUpsertRequest(tutor_id=8, content="Great progress")

        service.upsert_comment(db=MagicMock(), deliverable_id=5, payload=payload)

        args, kwargs = mock_repository.create.call_args
        # args: (db, tutor_id, deliverable_id, content)
        assert args[1] == 8
        assert args[2] == 5
        assert args[3] == "Great progress"



class TestUpsertCommentUpdate:

    def test_updates_comment_when_id_provided_and_exists(self, service, mock_repository, sample_comment):
        mock_repository.get_by_id.return_value = sample_comment
        mock_repository.update.return_value = sample_comment
        payload = CommentUpsertRequest(id=1, tutor_id=8, content="Updated content")

        result = service.upsert_comment(db=MagicMock(), deliverable_id=5, payload=payload)

        assert result.id == 1
        mock_repository.update.assert_called_once()
        mock_repository.create.assert_not_called()

    def test_raises_404_when_comment_id_does_not_exist(self, service, mock_repository):
        mock_repository.get_by_id.return_value = None
        payload = CommentUpsertRequest(id=999, tutor_id=8, content="Updated content")

        with pytest.raises(HTTPException) as exc_info:
            service.upsert_comment(db=MagicMock(), deliverable_id=5, payload=payload)

        assert exc_info.value.status_code == 404
        assert "999" in exc_info.value.detail
        mock_repository.update.assert_not_called()



class TestDeleteComment:

    def test_deletes_comment_when_exists(self, service, mock_repository, sample_comment):
        mock_repository.get_by_id.return_value = sample_comment

        service.delete_comment(db=MagicMock(), comment_id=1)

        mock_repository.delete.assert_called_once_with(mock_repository.delete.call_args[0][0], sample_comment)

    def test_raises_404_when_comment_does_not_exist(self, service, mock_repository):
        mock_repository.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            service.delete_comment(db=MagicMock(), comment_id=999)

        assert exc_info.value.status_code == 404
        assert "999" in exc_info.value.detail
        mock_repository.delete.assert_not_called()