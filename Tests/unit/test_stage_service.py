from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.core.schemas.stage import StageUpsert
from app.core.services.stage_service import StageService


def make_service(mocker):
    """Arma un StageService con StageRepository y CohortRepository mockeados."""
    mock_stage_repo = MagicMock()
    mock_cohort_repo = MagicMock()
    mocker.patch(
        "app.core.services.stage_service.StageRepository",
        return_value=mock_stage_repo,
    )
    mocker.patch(
        "app.core.services.stage_service.CohortRepository",
        return_value=mock_cohort_repo,
    )
    service = StageService(db=MagicMock())
    # Por defecto el cohort existe, salvo que el test diga lo contrario.
    mock_cohort_repo.get_by_id.return_value = MagicMock(id=1)
    return service, mock_stage_repo, mock_cohort_repo


# ---------- obtener etapas ----------

def test_get_all_devuelve_listado(mocker):
    service, mock_stage_repo, _ = make_service(mocker)
    mock_stage_repo.get_all.return_value = [MagicMock(id=1), MagicMock(id=2)]

    result = service.get_all()

    assert len(result) == 2
    mock_stage_repo.get_all.assert_called_once()


# ---------- actualizar (upsert) ----------

def test_upsert_crea_etapa_nueva_cuando_no_hay_id(mocker):
    service, mock_stage_repo, _ = make_service(mocker)
    nueva_etapa = MagicMock(id=1)
    mock_stage_repo.create.return_value = nueva_etapa
    data = StageUpsert(cohort_id=1, name="Planning", order=1)

    result = service.upsert(data)

    mock_stage_repo.create.assert_called_once_with(data)
    mock_stage_repo.update.assert_not_called()
    assert result == nueva_etapa


def test_upsert_actualiza_etapa_existente(mocker):
    service, mock_stage_repo, _ = make_service(mocker)
    etapa_existente = MagicMock(id=5)
    mock_stage_repo.get_by_id.return_value = etapa_existente
    mock_stage_repo.update.return_value = etapa_existente
    data = StageUpsert(id=5, cohort_id=1, name="Planning", order=1)

    result = service.upsert(data)

    mock_stage_repo.get_by_id.assert_called_once_with(5)
    mock_stage_repo.update.assert_called_once_with(etapa_existente, data)
    mock_stage_repo.create.assert_not_called()
    assert result == etapa_existente


def test_upsert_normaliza_id_cero_o_negativo_como_creacion(mocker):
    service, mock_stage_repo, _ = make_service(mocker)
    mock_stage_repo.create.return_value = MagicMock(id=1)
    data = StageUpsert(id=0, cohort_id=1, name="Planning", order=1)

    service.upsert(data)

    mock_stage_repo.create.assert_called_once()
    mock_stage_repo.get_by_id.assert_not_called()


def test_upsert_cohort_inexistente_tira_404(mocker):
    service, mock_stage_repo, mock_cohort_repo = make_service(mocker)
    mock_cohort_repo.get_by_id.return_value = None
    data = StageUpsert(cohort_id=999, name="Planning", order=1)

    with pytest.raises(HTTPException) as exc_info:
        service.upsert(data)

    assert exc_info.value.status_code == 404
    mock_stage_repo.create.assert_not_called()


def test_upsert_etapa_inexistente_tira_404(mocker):
    service, mock_stage_repo, _ = make_service(mocker)
    mock_stage_repo.get_by_id.return_value = None
    data = StageUpsert(id=999, cohort_id=1, name="Planning", order=1)

    with pytest.raises(HTTPException) as exc_info:
        service.upsert(data)

    assert exc_info.value.status_code == 404
    mock_stage_repo.update.assert_not_called()


# ---------- obtener entregables ----------

def test_get_expected_deliverables_exitoso(mocker):
    service, mock_stage_repo, _ = make_service(mocker)
    mock_stage_repo.get_by_id.return_value = MagicMock(id=1)
    mock_stage_repo.get_expected_deliverables.return_value = [MagicMock(), MagicMock()]

    result = service.get_expected_deliverables(1)

    assert len(result) == 2
    mock_stage_repo.get_expected_deliverables.assert_called_once_with(1)


def test_get_expected_deliverables_etapa_inexistente_tira_404(mocker):
    service, mock_stage_repo, _ = make_service(mocker)
    mock_stage_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.get_expected_deliverables(999)

    assert exc_info.value.status_code == 404
    mock_stage_repo.get_expected_deliverables.assert_not_called()


# ---------- validaciones ----------

def test_stage_upsert_requiere_cohort_id():
    with pytest.raises(ValidationError):
        StageUpsert(name="Planning", order=1)


def test_stage_upsert_order_debe_ser_numerico():
    with pytest.raises(ValidationError):
        StageUpsert(cohort_id=1, name="Planning", order="no-es-numero")
