import tempfile
import unittest
from pathlib import Path

from functional_test_cases import build, execution_policy, priority_for, stable_id


class FunctionalTestCasesTests(unittest.TestCase):
    def test_stable_id_is_deterministic(self):
        e = {"line": 10, "kind": "boton", "label": "Guardar", "target": ""}
        self.assertEqual(stable_id("repo", "index.html", e), stable_id("repo", "index.html", e))

    def test_admin_form_is_critical_and_controlled(self):
        e = {"kind": "formulario", "label": "Guardar noticia"}
        self.assertEqual(priority_for("administrativo", e), "P0_CRITICA")
        self.assertEqual(execution_policy("administrativo", e), "SESION_CONTROLADA_DATOS_PRUEBA")

    def test_navigation_is_medium_and_read_only(self):
        e = {"kind": "navegacion", "label": "Inicio"}
        self.assertEqual(priority_for("publico_o_auxiliar", e), "P2_MEDIA")
        self.assertEqual(execution_policy("publico_o_auxiliar", e), "AUTOMATIZABLE_LECTURA")

    def test_build_preserves_one_case_per_element(self):
        inventory = {
            "manifest": {"repositories": ["repo-a"]},
            "pages": [{
                "repo": "repo-a",
                "path": "index.html",
                "scope": "publico_o_auxiliar",
                "url_expected": "https://example.test/",
                "sha": "abc",
                "functional_elements": [
                    {"line": 1, "kind": "navegacion", "label": "Inicio", "target": "/", "expected_behavior": {"resolved_target": "https://example.test/"}},
                    {"line": 2, "kind": "boton", "label": "Compartir", "target": "", "expected_behavior": {"resolved_target": None}},
                ],
            }],
        }
        with tempfile.TemporaryDirectory() as tmp:
            status, result = build(inventory, Path(tmp))
            self.assertEqual(status, "completo")
            self.assertEqual(len(result["test_cases"]), 2)
            self.assertEqual(result["manifest"]["duplicate_ids"], 0)
            self.assertTrue((Path(tmp) / "functional-test-cases.json").exists())
            self.assertTrue((Path(tmp) / "Informe_fase_5_etapa_2.md").exists())


if __name__ == "__main__":
    unittest.main()
