import json
import tempfile
import unittest
from pathlib import Path

from security_diagnosis_validate import validate


class SecurityDiagnosisTests(unittest.TestCase):
    def load_report(self):
        return json.loads(Path('reports/fase-7-etapa-6-diagnostico-seguridad.json').read_text(encoding='utf-8'))

    def test_committed_report_valid(self):
        self.assertTrue(validate())

    def test_rejects_authorized_correction(self):
        data = self.load_report()
        data['correcciones_autorizadas'] = 1
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bad.json'
            p.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaises(AssertionError):
                validate(p)

    def test_rejects_stage7_started(self):
        data = self.load_report()
        data['etapa_7_iniciada'] = True
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bad.json'
            p.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaises(AssertionError):
                validate(p)

    def test_three_root_causes_only(self):
        data = self.load_report()
        self.assertEqual(data['hallazgos_diagnosticados'], 3)
        self.assertEqual(len(data['hallazgos']), 3)


if __name__ == '__main__':
    unittest.main()
