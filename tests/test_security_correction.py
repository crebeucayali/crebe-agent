import json
import tempfile
import unittest
from pathlib import Path

from security_correction_validate import validate


class SecurityCorrectionTests(unittest.TestCase):
    def load_report(self):
        return json.loads(Path('reports/fase-7-etapa-7-correccion-seguridad.json').read_text(encoding='utf-8'))

    def write_temp(self, data):
        f = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8')
        json.dump(data, f)
        f.close()
        return Path(f.name)

    def test_committed_report_valid(self):
        self.assertTrue(validate())

    def test_rejects_reopening_stage7(self):
        data = self.load_report()
        data['estado'] = 'ETAPA_7_EN_CURSO_CON_BLOQUEOS_CONTROLADOS'
        path = self.write_temp(data)
        with self.assertRaises(AssertionError):
            validate(path)

    def test_rejects_stage8_started_inside_stage7_report(self):
        data = self.load_report()
        data['resultado']['etapa_8_iniciada'] = True
        path = self.write_temp(data)
        with self.assertRaises(AssertionError):
            validate(path)

    def test_requires_rls_unchanged(self):
        data = self.load_report()
        data['resultado']['rls_modificado'] = True
        path = self.write_temp(data)
        with self.assertRaises(AssertionError):
            validate(path)

    def test_requires_free_plan_decision_for_exception(self):
        data = self.load_report()
        leaked = next(h for h in data['hallazgos'] if h['id'] == 'F7S4-AUTH-LEAKED-PASSWORD')
        leaked['decision_usuario'] = 'NO_DOCUMENTADA'
        path = self.write_temp(data)
        with self.assertRaises(AssertionError):
            validate(path)


if __name__ == '__main__':
    unittest.main()
