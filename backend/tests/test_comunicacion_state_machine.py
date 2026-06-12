"""Tests para la máquina de estados validate_transition (RN-15)."""

import pytest

from app.services.comunicacion_service import validate_transition


VALID_TRANSITIONS = [
    ("Pendiente", "Enviando"),
    ("Pendiente", "Cancelado"),
    ("Enviando", "Enviado"),
    ("Enviando", "Error"),
]

TERMINAL_STATES = ["Enviado", "Error", "Cancelado"]
ALL_STATES = ["Pendiente", "Enviando", "Enviado", "Error", "Cancelado"]


class TestTransicionesValidas:
    @pytest.mark.parametrize("actual,nueva", VALID_TRANSITIONS)
    def test_transicion_valida(self, actual, nueva):
        validate_transition(actual, nueva)


class TestTransicionesInvalidas:
    def test_desde_enviado_es_invalida(self):
        for nueva in ALL_STATES:
            with pytest.raises(ValueError, match="Transición inválida"):
                validate_transition("Enviado", nueva)

    def test_desde_error_es_invalida(self):
        for nueva in ALL_STATES:
            with pytest.raises(ValueError, match="Transición inválida"):
                validate_transition("Error", nueva)

    def test_desde_cancelado_es_invalida(self):
        for nueva in ALL_STATES:
            with pytest.raises(ValueError, match="Transición inválida"):
                validate_transition("Cancelado", nueva)

    def test_mismo_estado_es_invalido(self):
        for estado in ALL_STATES:
            with pytest.raises(ValueError, match="Transición inválida"):
                validate_transition(estado, estado)

    def test_transicion_inversa_pendiente_desde_enviando(self):
        with pytest.raises(ValueError, match="Transición inválida"):
            validate_transition("Enviando", "Pendiente")

    def test_transicion_arbitraria_es_invalida(self):
        with pytest.raises(ValueError, match="Transición inválida"):
            validate_transition("Pendiente", "Enviado")

    def test_transicion_estado_inexistente(self):
        with pytest.raises(ValueError, match="Transición inválida"):
            validate_transition("Pendiente", "Inventado")


class TestMensajeErrorDescriptivo:
    def test_mensaje_incluye_estados(self):
        with pytest.raises(ValueError) as exc:
            validate_transition("Pendiente", "Enviado")
        mensaje = str(exc.value)
        assert "Pendiente" in mensaje
        assert "Enviado" in mensaje
        assert "Transición inválida" in mensaje

    def test_mensaje_sugiere_transiciones_validas(self):
        with pytest.raises(ValueError) as exc:
            validate_transition("Pendiente", "Error")
        mensaje = str(exc.value)
        assert "Enviando" in mensaje
        assert "Cancelado" in mensaje
