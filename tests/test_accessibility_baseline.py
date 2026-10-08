import tempfile
import unittest
from pathlib import Path

from accessibility_baseline_scan import REPOS, baseline


class AccessibilityBaselineTests(unittest.TestCase):
    def test_structural_failures_and_candidates_are_separated(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for repo in REPOS:
                (root / repo).mkdir(parents=True)
                (root / repo / "index.html").write_text(
                    '<!doctype html><html><head><title>Pagina</title></head><body>'
                    '<img src="x.png"><button></button><input id="x"></body></html>',
                    encoding="utf-8",
                )
            data = baseline(root)
            self.assertEqual(data["universo"]["repositorios"], 8)
            self.assertEqual(data["universo"]["paginas_html_observadas_actualmente"], 8)
            by_id = {c["id"]: c for c in data["contratos"]}
            self.assertEqual(by_id["A11Y-CON-001"]["estado"], "INCUMPLIMIENTO_CONFIRMADO")
            self.assertEqual(by_id["A11Y-CON-003"]["estado"], "INCUMPLIMIENTO_CONFIRMADO")
            self.assertEqual(by_id["A11Y-CON-005"]["estado"], "REQUIERE_VERIFICACION_CONTROLADA")
            self.assertEqual(by_id["A11Y-CON-009"]["estado"], "REQUIERE_VERIFICACION_CONTROLADA")
            self.assertEqual(by_id["A11Y-CON-010"]["estado"], "REQUIERE_VERIFICACION_CONTROLADA")
            self.assertEqual(by_id["A11Y-CON-013"]["estado"], "REQUIERE_VERIFICACION_CONTROLADA")
            self.assertEqual(data["resumen_contratos"]["total"], 28)
            self.assertFalse(data["repositorios_eva_modificados"])
            self.assertTrue(data["guardrails"]["sin_correcciones"])

    def test_implicit_label_is_not_false_positive(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            html = ('<!doctype html><html lang="es"><head><title>Pagina unica</title></head><body>'
                    '<img src="x.png" alt="Descripcion"><button aria-label="Abrir"></button>'
                    '<label>Nombre<input id="x"></label></body></html>')
            for repo in REPOS:
                (root / repo).mkdir(parents=True)
                (root / repo / "index.html").write_text(html, encoding="utf-8")
            data = baseline(root)
            by_id = {c["id"]: c for c in data["contratos"]}
            self.assertEqual(by_id["A11Y-CON-001"]["estado"], "CUMPLE")
            self.assertEqual(by_id["A11Y-CON-003"]["estado"], "CUMPLE")
            self.assertEqual(by_id["A11Y-CON-005"]["estado"], "REQUIERE_VERIFICACION_CONTROLADA")
            self.assertEqual(by_id["A11Y-CON-005"]["evidencia"]["cantidad_candidatos"], 0)
            self.assertEqual(by_id["A11Y-CON-009"]["estado"], "REQUIERE_VERIFICACION_CONTROLADA")
            self.assertEqual(by_id["A11Y-CON-010"]["estado"], "REQUIERE_VERIFICACION_CONTROLADA")


if __name__ == "__main__":
    unittest.main()
