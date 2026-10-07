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

    def test_rejects_false_completion(self):
        data = self.load_report()
        data['estado'] = 'ETAPA_7_COMPLETADA_CORRECCION_SEGURIDAD'
        path = self.write_temp(data)
        with self.assertRaises(AssertionError):
            validate(path)

    def test_rejects_stage8_started(self):
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


if __name__ == '__main__':
    unittest.main()
