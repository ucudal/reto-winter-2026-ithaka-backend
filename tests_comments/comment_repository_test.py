import pytest

from app.core.models.comment import Comment
from app.core.repositories.comment_repository import CommentRepository


@pytest.fixture
def repository():
    return CommentRepository()



class TestListByDeliverable:

    def test_returns_only_comments_of_that_deliverable(self, db_session, repository):
        db_session.add_all([
            Comment(tutor_id=8, deliverable_id=5, content="Comment A"),
            Comment(tutor_id=8, deliverable_id=5, content="Comment B"),
            Comment(tutor_id=8, deliverable_id=99, content="Comment C"),
        ])
        db_session.commit()

        result = repository.list_by_deliverable(db_session, 5)

        assert len(result) == 2
        assert all(c.deliverable_id == 5 for c in result)

    def test_returns_empty_list_when_no_comments(self, db_session, repository):
        result = repository.list_by_deliverable(db_session, 999)

        assert result == []



class TestGetById:

    def test_returns_comment_when_exists(self, db_session, repository):
        comment = Comment(tutor_id=8, deliverable_id=5, content="Needs review")
        db_session.add(comment)
        db_session.commit()

        result = repository.get_by_id(db_session, comment.id)

        assert result is not None
        assert result.content == "Needs review"

    def test_returns_none_when_does_not_exist(self, db_session, repository):
        result = repository.get_by_id(db_session, 999)

        assert result is None



class TestCreate:

    def test_creates_comment_with_correct_fields(self, db_session, repository):
        result = repository.create(db_session, tutor_id=8, deliverable_id=5, content="New comment")

        assert result.id is not None
        assert result.tutor_id == 8
        assert result.deliverable_id == 5
        assert result.content == "New comment"

    def test_persists_comment_in_database(self, db_session, repository):
        created = repository.create(db_session, tutor_id=8, deliverable_id=5, content="New comment")

        found = repository.get_by_id(db_session, created.id)

        assert found is not None
        assert found.id == created.id



class TestUpdate:

    def test_updates_tutor_id_and_content(self, db_session, repository):
        comment = Comment(tutor_id=8, deliverable_id=5, content="Original content")
        db_session.add(comment)
        db_session.commit()

        result = repository.update(db_session, comment, tutor_id=14, content="Updated content")

        assert result.tutor_id == 14
        assert result.content == "Updated content"

    def test_does_not_change_deliverable_id(self, db_session, repository):
        comment = Comment(tutor_id=8, deliverable_id=5, content="Original content")
        db_session.add(comment)
        db_session.commit()

        result = repository.update(db_session, comment, tutor_id=14, content="Updated content")

        assert result.deliverable_id == 5



class TestDelete:

    def test_removes_comment_from_database(self, db_session, repository):
        comment = Comment(tutor_id=8, deliverable_id=5, content="To be deleted")
        db_session.add(comment)
        db_session.commit()
        comment_id = comment.id

        repository.delete(db_session, comment)

        assert repository.get_by_id(db_session, comment_id) is None