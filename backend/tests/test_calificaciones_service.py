"""Tests para CalificacionesService — _es_aprobado y detección de columnas (C-10)."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.calificacion import Calificacion
from app.models.umbral_materia import UmbralMateria
from app.schemas.calificaciones import ColumnaDetectada
from app.services.calificaciones_service import CalificacionesService


class TestEsAprobado:
    def test_numeric_above_threshold(self):
        cal = Calificacion(nota_numerica=75.0, nota_textual=None)
        umbral = UmbralMateria(umbral_pct=60)
        result = CalificacionesService._es_aprobado(cal, umbral)
        assert result is True

    def test_numeric_below_threshold(self):
        cal = Calificacion(nota_numerica=55.0, nota_textual=None)
        umbral = UmbralMateria(umbral_pct=60)
        result = CalificacionesService._es_aprobado(cal, umbral)
        assert result is False

    def test_numeric_at_threshold(self):
        cal = Calificacion(nota_numerica=60.0, nota_textual=None)
        umbral = UmbralMateria(umbral_pct=60)
        result = CalificacionesService._es_aprobado(cal, umbral)
        assert result is True

    def test_textual_satisfactorio(self):
        cal = Calificacion(nota_numerica=None, nota_textual="Satisfactorio")
        umbral = UmbralMateria(valores_aprobatorios=["Satisfactorio", "Supera lo esperado"])
        result = CalificacionesService._es_aprobado(cal, umbral)
        assert result is True

    def test_textual_not_approved(self):
        cal = Calificacion(nota_numerica=None, nota_textual="Regular")
        umbral = UmbralMateria(valores_aprobatorios=["Satisfactorio", "Supera lo esperado"])
        result = CalificacionesService._es_aprobado(cal, umbral)
        assert result is False

    def test_no_umbral_uses_default_60(self):
        cal = Calificacion(nota_numerica=60.0, nota_textual=None)
        result = CalificacionesService._es_aprobado(cal, None)
        assert result is True

    def test_no_umbral_uses_default_55_fails(self):
        cal = Calificacion(nota_numerica=55.0, nota_textual=None)
        result = CalificacionesService._es_aprobado(cal, None)
        assert result is False

    def test_no_nota_at_all(self):
        cal = Calificacion(nota_numerica=None, nota_textual=None)
        umbral = UmbralMateria(umbral_pct=60)
        result = CalificacionesService._es_aprobado(cal, umbral)
        assert result is False

    def test_custom_umbral_70(self):
        cal = Calificacion(nota_numerica=70.0, nota_textual=None)
        umbral = UmbralMateria(umbral_pct=70)
        result = CalificacionesService._es_aprobado(cal, umbral)
        assert result is True

    def test_custom_umbral_70_fails_at_65(self):
        cal = Calificacion(nota_numerica=65.0, nota_textual=None)
        umbral = UmbralMateria(umbral_pct=70)
        result = CalificacionesService._es_aprobado(cal, umbral)
        assert result is False

    def test_textual_default_values_when_no_umbral(self):
        cal = Calificacion(nota_numerica=None, nota_textual="Supera lo esperado")
        result = CalificacionesService._es_aprobado(cal, None)
        assert result is True

    def test_textual_default_values_when_umbral_has_no_valores(self):
        cal = Calificacion(nota_numerica=None, nota_textual="Satisfactorio")
        umbral = UmbralMateria(umbral_pct=60, valores_aprobatorios=[])
        result = CalificacionesService._es_aprobado(cal, umbral)
        assert result is False


class TestDetectColumnTypes:
    def test_detect_real_suffix(self):
        svc = _make_service()
        headers = ["Nombre", "Apellidos", "Examen (Real)", "TP (Real)"]
        columns = svc._detect_column_types(headers)
        assert len(columns) == 4
        examen = next(c for c in columns if c.name == "Examen (Real)")
        assert examen.tipo == "numerica"
        assert examen.aprobatorio is False
        tp = next(c for c in columns if c.name == "TP (Real)")
        assert tp.tipo == "numerica"
        assert tp.aprobatorio is False

    def test_detect_satisfactorio_column(self):
        svc = _make_service()
        headers = ["Nombre", "Satisfactorio"]
        columns = svc._detect_column_types(headers)
        sat = next(c for c in columns if c.name == "Satisfactorio")
        assert sat.tipo == "textual"
        assert sat.aprobatorio is True

    def test_detect_supera_lo_esperado(self):
        svc = _make_service()
        headers = ["Nombre", "Supera lo esperado"]
        columns = svc._detect_column_types(headers)
        supera = next(c for c in columns if c.name == "Supera lo esperado")
        assert supera.tipo == "textual"
        assert supera.aprobatorio is True

    def test_regular_column_is_textual_not_aprobatorio(self):
        svc = _make_service()
        headers = ["Nombre", "Comentario", "Nota"]
        columns = svc._detect_column_types(headers)
        for c in columns:
            if c.name == "Comentario":
                assert c.tipo == "textual"
                assert c.aprobatorio is False

    def test_mixed_columns(self):
        svc = _make_service()
        headers = ["Practica (Real)", "Satisfactorio", "Comentario"]
        columns = svc._detect_column_types(headers)
        prac = next(c for c in columns if c.name == "Practica (Real)")
        assert prac.tipo == "numerica"
        assert prac.aprobatorio is False
        sat = next(c for c in columns if c.name == "Satisfactorio")
        assert sat.tipo == "textual"
        assert sat.aprobatorio is True
        com = next(c for c in columns if c.name == "Comentario")
        assert com.tipo == "textual"
        assert com.aprobatorio is False


def _make_service():
    mock_session = MagicMock()
    return CalificacionesService(mock_session, __import__("uuid").uuid4())
