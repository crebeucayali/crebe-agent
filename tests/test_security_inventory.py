import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports' / 'fase-7-etapa-1-inventario-seguridad.json'
TRACKING = ROOT / 'tracking' / 'fase-7-etapa-1.json'


class SecurityInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(REPORT.read_text(encoding='utf-8'))
        cls.tracking = json.loads(TRACKING.read_text(encoding='utf-8'))

    def test_read_only_guards(self):
        rules = self.report['reglas_de_inventario']
        self.assertTrue(rules['no_secret_values_in_report'])
        self.assertTrue(rules['no_risk_severity_assigned_yet'])
        self.assertTrue(rules['no_corrections_authorized'])
        self.assertFalse(rules['supabase_modified'])
        self.assertFalse(rules['eva_repositories_modified'])

    def test_inventory_counts(self):
        supabase = self.report['supabase']
        self.assertEqual(supabase['objetos_catalogados'], 21)
        self.assertEqual(supabase['politicas_rls_catalogadas'], 36)
        self.assertEqual(supabase['funciones_publicas_security_definer'], 0)
        self.assertEqual(supabase['funciones_private_catalogadas'], 24)
        self.assertEqual(supabase['funciones_private_security_definer'], 19)

    def test_sensitive_key_classification(self):
        github = self.report['github']
        self.assertFalse(github['service_role_literal_detectado'])
        self.assertFalse(github['sb_secret_literal_detectado'])
        self.assertIn('publicable', github['publishable_key'].lower())

    def test_surface_ids_unique_and_stage_two_closed(self):
        ids = [s['id'] for s in self.report['superficies_a_contratar_en_etapa_2']]
        self.assertEqual(len(ids), 6)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertFalse(self.tracking['etapa_2_iniciada'])


if __name__ == '__main__':
    unittest.main()
