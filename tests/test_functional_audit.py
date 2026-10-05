import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from functional_audit import build, classify_network, preset_status


class FunctionalAuditTests(unittest.TestCase):
    def test_admin_case_is_blocked_by_dependency(self):
        case = {"execution_policy": "SESION_CONTROLADA_DATOS_PRUEBA"}
        status, _ = preset_status(case)
        self.assertEqual(status, "BLOQUEADO_POR_DEPENDENCIA")

    def test_browser_case_requires_manual_verification(self):
        case = {"execution_policy": "NAVEGADOR_INSTRUMENTADO_SIN_PERSISTENCIA"}
        status, _ = preset_status(case)
        self.assertEqual(status, "REQUIERE_VERIFICACION_MANUAL")

    def test_404_is_confirmed_failure(self):
        case = {"kind": "navegacion", "page_url": "https://example.test/", "target": "/x"}
        status, _ = classify_network(case, {"ok": False, "status": 404})
        self.assertEqual(status, "FALLO_CONFIRMADO")

    def test_build_processes_all_cases(self):
        cases = {
            "test_cases": [
                {"id": "1", "repo": "repo", "page_url": "https://example.test/", "kind": "navegacion", "target": "/ok", "execution_policy": "AUTOMATIZABLE_LECTURA"},
                {"id": "2", "repo": "repo", "page_url": "https://example.test/", "kind": "boton", "target": "", "execution_policy": "NAVEGADOR_INSTRUMENTADO_SIN_PERSISTENCIA"},
            ]
        }
        fake = {"ok": True, "status": 200, "final_url": "https://example.test/ok", "content_type": "text/html", "body": "<html></html>", "error": None}
        with tempfile.TemporaryDirectory() as tmp, patch("functional_audit.request_url", return_value=fake):
            status, result = build(cases, Path(tmp), workers=1)
            self.assertEqual(status, "completo")
            self.assertEqual(result["summary"]["total"], 2)
            self.assertTrue((Path(tmp) / "functional-audit.json").exists())
            self.assertTrue((Path(tmp) / "Informe_fase_5_etapa_3.md").exists())


if __name__ == "__main__":
    unittest.main()
