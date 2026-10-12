import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import security_monitor


class SecurityMonitorTests(unittest.TestCase):
    def test_baseline_is_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = security_monitor.run(tmp)
            self.assertEqual(result['estado'], 'SEGURO', msg=json.dumps(result, ensure_ascii=False))
            self.assertEqual(result['alertas'], [])
            self.assertEqual(result['state_source'], 'state/current.json')
            self.assertEqual(result['security_phase_status'], 'MONITOREO_SEGURIDAD_ACTIVO')
            self.assertEqual(result['security_auth_source'], 'tracking/fase-7-etapa-7.json')

    def test_current_state_is_operational_source(self):
        current = json.loads(Path('state/current.json').read_text(encoding='utf-8'))
        current['phases']['fase_7']['status'] = 'ESTADO_DE_PRUEBA_NO_ACTIVO'
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / 'current.json'
            state_path.write_text(json.dumps(current, ensure_ascii=False), encoding='utf-8')
            with patch.object(security_monitor, 'CURRENT_STATE', state_path):
                result = security_monitor.run(Path(tmp) / 'out')
        self.assertEqual(result['estado'], 'ALERTA')
        self.assertIn(
            'El estado canónico ya no registra el monitoreo de seguridad como activo.',
            result['alertas'],
        )

    def test_current_state_authentication_is_operational_source(self):
        current = json.loads(Path('state/current.json').read_text(encoding='utf-8'))
        current['phases']['fase_7']['authentication']['master'] = 'ESTADO_DE_PRUEBA_SIN_AAL2'
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / 'current.json'
            state_path.write_text(json.dumps(current, ensure_ascii=False), encoding='utf-8')
            with patch.object(security_monitor, 'CURRENT_STATE', state_path):
                result = security_monitor.run(Path(tmp) / 'out')
        self.assertEqual(result['estado'], 'ALERTA')
        self.assertIn('El master ya no conserva AAL2/MFA como requisito.', result['alertas'])

    def test_expected_free_plan_exception_is_configured(self):
        cfg = json.loads(Path('config/security-monitor.json').read_text(encoding='utf-8'))
        ids = {x['id'] for x in cfg['accepted_exceptions']}
        self.assertIn('F7S4-AUTH-LEAKED-PASSWORD', ids)

    def test_master_mfa_remains_required(self):
        current = json.loads(Path('state/current.json').read_text(encoding='utf-8'))
        auth = current['phases']['fase_7']['authentication']
        self.assertEqual(auth['master'], 'AUTHENTICATED_PLUS_AAL2_MFA')
        self.assertFalse(auth['mfa_obligatorio_editores'])


if __name__ == '__main__':
    unittest.main()
