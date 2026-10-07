import json
import tempfile
import unittest
from pathlib import Path

import security_monitor


class SecurityMonitorTests(unittest.TestCase):
    def test_baseline_is_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = security_monitor.run(tmp)
            self.assertEqual(result['estado'], 'SEGURO')
            self.assertEqual(result['alertas'], [])

    def test_expected_free_plan_exception_is_configured(self):
        cfg = json.loads(Path('config/security-monitor.json').read_text(encoding='utf-8'))
        ids = {x['id'] for x in cfg['accepted_exceptions']}
        self.assertIn('F7S4-AUTH-LEAKED-PASSWORD', ids)

    def test_master_mfa_remains_required(self):
        tracking = json.loads(Path('tracking/fase-7-etapa-7.json').read_text(encoding='utf-8'))
        self.assertEqual(tracking['modelo_autenticacion_confirmado']['master'], 'AUTHENTICATED_PLUS_AAL2_MFA')
        self.assertFalse(tracking['modelo_autenticacion_confirmado']['mfa_obligatorio_editores'])


if __name__ == '__main__':
    unittest.main()
