import json
import unittest
from pathlib import Path

import accessibility_contracts_validate


class AccessibilityContractsTests(unittest.TestCase):
    def test_validate_contracts(self):
        accessibility_contracts_validate.validate()

    def test_two_contracts_per_surface(self):
        report = json.loads(Path('reports/fase-8-etapa-2-contratos-accesibilidad.json').read_text(encoding='utf-8'))
        scope = json.loads(Path('config/fase-8-accessibility-scope.json').read_text(encoding='utf-8'))
        counts = {surface: 0 for surface in scope['superficies']}
        for contract in report['contratos']:
            counts[contract['superficie']] += 1
        self.assertTrue(all(value == 2 for value in counts.values()))

    def test_no_corrections_or_findings(self):
        report = json.loads(Path('reports/fase-8-etapa-2-contratos-accesibilidad.json').read_text(encoding='utf-8'))
        self.assertEqual(report['hallazgos_confirmados'], 0)
        self.assertEqual(report['severidades_asignadas'], 0)
        self.assertEqual(report['correcciones_aplicadas'], 0)
        self.assertFalse(report['repositorios_eva_modificados'])


if __name__ == '__main__':
    unittest.main()
