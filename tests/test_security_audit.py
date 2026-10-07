import copy
import json
import unittest
from pathlib import Path

import security_audit_validate as validator

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "fase-7-etapa-3-linea-base-seguridad.json"


class SecurityAuditTests(unittest.TestCase):
    def test_committed_audit_is_valid(self):
        self.assertEqual(validator.validate(), [])

    def test_all_26_contracts_are_accounted_for(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(len(report["resultados"]), 26)
        self.assertEqual(sum(report["resumen"].values()), 26)

    def test_confirmed_findings_are_exact(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(set(report["hallazgos_confirmados_ids"]), {
            "SEC-CON-001","SEC-CON-003","SEC-CON-004","SEC-CON-011","SEC-CON-026"
        })

    def test_controlled_tests_are_not_reported_as_confirmed(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        confirmed = set(report["hallazgos_confirmados_ids"])
        controlled = set(report["pruebas_controladas_pendientes_ids"])
        self.assertTrue(confirmed.isdisjoint(controlled))

    def test_read_only_guardrails(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["modo"], "READ_ONLY")
        self.assertFalse(report["correccion_autorizada"])
        self.assertFalse(report["supabase_modificado"])
        self.assertFalse(report["repositorios_eva_modificados"])


if __name__ == "__main__":
    unittest.main()
