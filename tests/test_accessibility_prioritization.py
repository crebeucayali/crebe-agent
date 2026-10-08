import json
import unittest
from pathlib import Path


class AccessibilityPrioritizationTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads(Path("reports/fase-8-etapa-4-priorizacion-accesibilidad.json").read_text(encoding="utf-8"))

    def test_priorities_cover_only_pending_contracts(self):
        groups = self.report["grupos"]
        contracts = [cid for group in groups for cid in group["contratos"]]
        self.assertEqual(len(contracts), 26)
        self.assertEqual(len(set(contracts)), 26)
        self.assertNotIn("A11Y-CON-001", contracts)
        self.assertNotIn("A11Y-CON-003", contracts)
        self.assertEqual(self.report["prioridades_verificacion"], {"P0": 11, "P1": 13, "P2": 2})

    def test_no_unconfirmed_failure_is_promoted_or_corrected(self):
        self.assertEqual(self.report["incumplimientos_confirmados"], 0)
        self.assertEqual(self.report["hallazgos_confirmados_nuevos"], 0)
        self.assertEqual(self.report["severidades_de_fallos_asignadas"], 0)
        self.assertEqual(self.report["correcciones_aplicadas"], 0)
        self.assertFalse(self.report["repositorios_eva_modificados"])
        self.assertFalse(self.report["supabase_modificado"])
        self.assertFalse(self.report["etapa_5_iniciada"])


if __name__ == "__main__":
    unittest.main()
