import json
from pathlib import Path
import tempfile
import unittest

from security_permission_tests_validate import validate


class SecurityPermissionTests(unittest.TestCase):
    def load_report(self):
        return json.loads(Path('reports/fase-7-etapa-5-pruebas-permisos.json').read_text(encoding='utf-8'))

    def write_bad(self, data):
        tmp = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8')
        with tmp:
            json.dump(data, tmp)
        return Path(tmp.name)

    def test_committed_report_valid(self):
        self.assertTrue(validate())

    def test_detects_failed_contract(self):
        data = self.load_report()
        data['pruebas'][0]['resultado'] = 'FAIL'
        p = self.write_bad(data)
        with self.assertRaises(AssertionError):
            validate(p)
        p.unlink(missing_ok=True)

    def test_detects_residue(self):
        data = self.load_report()
        data['resultado']['residuos'] = 1
        p = self.write_bad(data)
        with self.assertRaises(AssertionError):
            validate(p)
        p.unlink(missing_ok=True)

    def test_detects_stage6_started(self):
        data = self.load_report()
        data['etapa_6_iniciada'] = True
        p = self.write_bad(data)
        with self.assertRaises(AssertionError):
            validate(p)
        p.unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
