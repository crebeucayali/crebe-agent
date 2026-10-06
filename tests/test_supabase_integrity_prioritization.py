import json
import unittest
from pathlib import Path

from supabase_integrity_prioritization_validate import validate


class TestIntegrityPrioritization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(Path('reports/fase-6-etapa-4-priorizacion.json').read_text(encoding='utf-8'))

    def test_report_validates(self):
        validate(self.data)

    def test_zero_findings_when_zero_inconsistencies(self):
        r = self.data['resumen']
        self.assertEqual(r['inconsistencias_confirmadas'], 0)
        self.assertEqual(r['hallazgos_prioritarios'], 0)
        self.assertEqual(self.data['hallazgos_priorizados'], [])

    def test_storage_candidates_are_not_findings(self):
        item = next(x for x in self.data['observaciones_no_hallazgo'] if x['id'] == 'STORAGE-CANDIDATOS-REVISION')
        self.assertFalse(item['es_inconsistencia'])
        self.assertEqual(item['cantidad'], 24)

    def test_security_dependency_is_separate(self):
        item = next(x for x in self.data['observaciones_no_hallazgo'] if x['id'] == 'SEC-DEPENDENCY-001')
        self.assertEqual(item['destino'], 'Fase Seguridad y permisos')
        self.assertFalse(item['es_inconsistencia'])


if __name__ == '__main__':
    unittest.main()
