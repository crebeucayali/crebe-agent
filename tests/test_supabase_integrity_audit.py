import json
import unittest
from pathlib import Path

from supabase_integrity_audit_validate import validate

ROOT = Path(__file__).resolve().parents[1]


class AuditIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads((ROOT / 'reports' / 'fase-6-etapa-3-integridad.json').read_text(encoding='utf-8'))

    def test_validator(self):
        self.assertTrue(validate())

    def test_all_contracts_are_accounted_for(self):
        self.assertEqual(self.report['resumen']['contratos_totales'], 42)
        self.assertEqual(len(self.report['resultados']), 42)

    def test_no_confirmed_integrity_failures(self):
        self.assertEqual(self.report['resumen']['INCONSISTENCIA_CONFIRMADA'], 0)
        self.assertEqual(self.report['resumen']['hallazgos_confirmados'], 0)

    def test_read_only_closure(self):
        self.assertFalse(self.report['resumen']['supabase_modificado'])
        self.assertFalse(self.report['resumen']['repositorios_eva_modificados'])

    def test_storage_missing_references_zero(self):
        storage = self.report['evidencia_clave']['storage']
        self.assertEqual(storage['referencias_faltantes'], 0)
        self.assertEqual(storage['objetos_no_referenciados_candidatos_revision'], 24)


if __name__ == '__main__':
    unittest.main()
