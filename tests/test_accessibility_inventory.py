import json
import unittest
from pathlib import Path

import accessibility_inventory_validate


class AccessibilityInventoryTests(unittest.TestCase):
    def test_inventory_validator(self):
        accessibility_inventory_validate.validate()

    def test_no_corrections_in_stage_1(self):
        report = json.loads(Path('reports/fase-8-etapa-1-inventario-accesibilidad.json').read_text(encoding='utf-8'))
        self.assertEqual(report['hallazgos_confirmados'], 0)
        self.assertEqual(report['correcciones_autorizadas'], 0)
        self.assertFalse(report['repositorios_eva_modificados'])

    def test_surface_catalog_is_complete(self):
        report = json.loads(Path('reports/fase-8-etapa-1-inventario-accesibilidad.json').read_text(encoding='utf-8'))
        self.assertEqual(report['superficies_inventariadas'], 14)
        self.assertEqual(len(report['superficies']), 14)


if __name__ == '__main__':
    unittest.main()
