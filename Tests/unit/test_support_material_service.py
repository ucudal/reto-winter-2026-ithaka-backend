from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.core.schemas.support_material import SupportMaterialUpsertRequest
from app.core.services.support_material_service import SupportMaterialService


def make_service():
    mock_repo = MagicMock()
    service = SupportMaterialService(repository=mock_repo)
    return service, mock_repo


# ---------- obtener materiales ----------

def test_list_materials_filtra_por_stage(mock_db):
    service, mock_repo = make_service()
    mock_repo.list.return_value = [
        MagicMock(id=1, stage_id=3, title="Guia 1", url="http://x.com"),
    ]

    result = service.list_materials(mock_db, stage_id=3)

    mock_repo.list.assert_called_once_with(
        mock_db, stage_id=3, search=None, page=1, page_size=10
    )
    assert len(result) == 1
    assert result[0].stage_id == 3


def test_list_materials_sin_resultados_devuelve_lista_vacia(mock_db):
    service, mock_repo = make_service()
    mock_repo.list.return_value = []

    result = service.list_materials(mock_db, stage_id=99)

    assert result == []


def test_get_material_exitoso(mock_db):
    service, mock_repo = make_service()
    mock_repo.get_by_id.return_value = MagicMock(
        id=1, stage_id=1, title="Guia", url="http://x.com"
    )

    result = service.get_material(mock_db, 1)

    assert result.id == 1


def test_get_material_inexistente_tira_404(mock_db):
    service, mock_repo = make_service()
    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.get_material(mock_db, 999)

    assert exc_info.value.status_code == 404


# ---------- validaciones ----------

def test_support_material_upsert_requiere_url():
    with pytest.raises(ValidationError):
        SupportMaterialUpsertRequest(stage_id=1, title="Guia")
