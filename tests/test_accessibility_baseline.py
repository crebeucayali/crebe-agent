import json
import tempfile
import unittest
from pathlib import Path

from accessibility_baseline_scan import REPOS, baseline


class AccessibilityBaselineTests(unittest.TestCase):
    def test_objective_findings_and_controlled_contracts(self):
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
            self.assertEqual(data["universo_observado"]["repositorios"], 8)
            self.assertEqual(data["universo_observado"]["paginas_html"], 8)
            by_id = {c["id"]: c for c in data["contratos"]}
            self.assertEqual(by_id["A11Y-CON-001"]["estado"], "INCUMPLIMIENTO_CONFIRMADO")
            self.assertEqual(by_id["A11Y-CON-003"]["estado"], "INCUMPLIMIENTO_CONFIRMADO")
            self.assertEqual(by_id["A11Y-CON-005"]["estado"], "INCUMPLIMIENTO_CONFIRMADO")
            self.assertEqual(by_id["A11Y-CON-009"]["estado"], "INCUMPLIMIENTO_CONFIRMADO")
            self.assertEqual(by_id["A11Y-CON-013"]["estado"], "REQUIERE_VERIFICACION_CONTROLADA")
            self.assertEqual(data["resumen_contratos"]["total"], 28)
            self.assertFalse(data["repositorios_eva_modificados"])
            self.assertTrue(data["guardrails"]["sin_correcciones"])

    def test_clean_static_objective_checks_can_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            html = ('<!doctype html><html lang="es"><head><title>Pagina unica</title></head><body>'
                    '<img src="x.png" alt="Descripcion"><button aria-label="Abrir"></button>'
                    '<label for="x">Nombre</label><input id="x"></body></html>')
            for repo in REPOS:
                (root / repo).mkdir(parents=True)
                (root / repo / "index.html").write_text(html, encoding="utf-8")
            data = baseline(root)
            by_id = {c["id"]: c for c in data["contratos"]}
            for cid in ("A11Y-CON-001", "A11Y-CON-003", "A11Y-CON-005", "A11Y-CON-009", "A11Y-CON-010"):
                self.assertEqual(by_id[cid]["estado"], "CUMPLE")


if __name__ == "__main__":
    unittest.main()
