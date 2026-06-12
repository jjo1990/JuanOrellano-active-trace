"""Tests para render_template con variables de sustitución."""

import pytest

from app.services.comunicacion_service import render_template


class TestRenderTemplateBasico:
    def test_variable_nombre(self):
        result = render_template("Hola {{nombre}}", {"nombre": "Ana"})
        assert result == "Hola Ana"

    def test_variable_materia(self):
        result = render_template(
            "Materia: {{materia}}", {"materia": "Programación I"}
        )
        assert result == "Materia: Programación I"

    def test_variable_nota_promedio(self):
        result = render_template(
            "Nota: {{nota_promedio}}", {"nota_promedio": "75"}
        )
        assert result == "Nota: 75"

    def test_variable_actividades_pendientes(self):
        result = render_template(
            "Faltan: {{actividades_pendientes}}",
            {"actividades_pendientes": "TP1, TP2"},
        )
        assert result == "Faltan: TP1, TP2"

    def test_variable_link_materia(self):
        result = render_template(
            "Accedé: {{link_materia}}",
            {"link_materia": "https://aula.ejemplo.com"},
        )
        assert result == "Accedé: https://aula.ejemplo.com"

    def test_multiples_variables(self):
        template = "Hola {{nombre}}, tu nota en {{materia}} es {{nota_promedio}}"
        context = {"nombre": "Juan", "materia": "Matemática", "nota_promedio": "80"}
        result = render_template(template, context)
        assert result == "Hola Juan, tu nota en Matemática es 80"


class TestRenderTemplateVariablesNoDefinidas:
    def test_variable_faltante_se_preserva(self):
        result = render_template("Hola {{no_existe}}", {})
        assert result == "Hola {{no_existe}}"

    def test_mezcla_definidas_y_no(self):
        result = render_template(
            "{{nombre}} y {{desconocida}}",
            {"nombre": "Ana"},
        )
        assert result == "Ana y {{desconocida}}"


class TestRenderTemplateMultiplesOcurrencias:
    def test_misma_variable_repetida(self):
        template = "{{nombre}}, tu nota es {{nota}}. Saludos, {{nombre}}"
        context = {"nombre": "Ana", "nota": "8"}
        result = render_template(template, context)
        assert result == "Ana, tu nota es 8. Saludos, Ana"


class TestRenderTemplateSinVariables:
    def test_sin_variables(self):
        result = render_template("Hola mundo", {})
        assert result == "Hola mundo"

    def test_contexto_no_usado(self):
        result = render_template("Sin variables", {"nombre": "Ana"})
        assert result == "Sin variables"


class TestRenderTemplateEdgeCases:
    def test_template_vacio(self):
        result = render_template("", {"nombre": "Ana"})
        assert result == ""

    def test_contexto_vacio(self):
        result = render_template("Hola {{mundo}}", {})
        assert result == "Hola {{mundo}}"

    def test_no_confunde_variables_similares(self):
        """{{nombre}} no debe reemplazar parcialmente {{nombre_completo}}."""
        template = "{{nombre}}: {{nombre_completo}}"
        context = {"nombre": "Ana", "nombre_completo": "Ana García"}
        result = render_template(template, context)
        assert result == "Ana: Ana García"

    def test_llaves_simples_no_se_tocan(self):
        result = render_template("{nombre}", {"nombre": "Ana"})
        assert result == "{nombre}"
