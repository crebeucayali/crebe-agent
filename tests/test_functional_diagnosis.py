import tempfile
import unittest
from pathlib import Path

from functional_diagnosis import build


class FunctionalDiagnosisTests(unittest.TestCase):
    def test_known_target_is_ready_for_correction(self):
        prioritization = {"findings": [{"id": "A", "target": "old", "priority": "P1_ALTA", "severity": "ALTO", "case_count": 2, "affected_pages": []}]}
        evidence = {"diagnoses": {"A": {"root_cause": "OBSOLETA", "diagnosis": "Ruta antigua", "correct_target": "new", "technical_action_class": "REEMPLAZAR", "confidence": "ALTA"}}}
        with tempfile.TemporaryDirectory() as tmp:
            status, result = build(prioritization, evidence, Path(tmp))
            self.assertEqual(status, "completo")
            self.assertEqual(result["diagnoses"][0]["stage_5_status"], "DIAGNOSTICADO_LISTO_PARA_CORRECCION")

    def test_missing_target_requires_documented_decision(self):
        prioritization = {"findings": [{"id": "A", "target": "old", "priority": "P1_ALTA", "severity": "ALTO", "case_count": 1, "affected_pages": []}]}
        evidence = {"diagnoses": {"A": {"root_cause": "HUERFANA", "diagnosis": "Sin reemplazo", "correct_target": None, "technical_action_class": "RETIRAR_O_REEMPLAZAR", "decision_required": "Definir destino"}}}
        with tempfile.TemporaryDirectory() as tmp:
            status, result = build(prioritization, evidence, Path(tmp))
            self.assertEqual(status, "completo")
            self.assertEqual(result["diagnoses"][0]["stage_5_status"], "DIAGNOSTICADO_REQUIERE_DECISION_FUNCIONAL")

    def test_missing_diagnosis_is_incomplete(self):
        prioritization = {"findings": [{"id": "A", "target": "old"}]}
        with tempfile.TemporaryDirectory() as tmp:
            status, result = build(prioritization, {"diagnoses": {}}, Path(tmp))
            self.assertEqual(status, "incompleto")
            self.assertEqual(result["manifest"]["missing_diagnoses"], ["A"])


if __name__ == "__main__":
    unittest.main()
