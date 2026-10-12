import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / 'config/security-monitor.json'
CURRENT_STATE = ROOT / 'state/current.json'
REPORT = ROOT / 'reports/fase-7-etapa-7-correccion-seguridad.json'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def scan_for_literal_secrets():
    hits = []
    pattern = re.compile(r'sb_secret_[A-Za-z0-9_-]{20,}')
    excluded_dirs = {'.git', '__pycache__', 'docs', 'reports', 'tracking', 'tests'}
    allowed_suffixes = {'.py', '.js', '.ts', '.json', '.yml', '.yaml', '.html', '.css', '.sql'}
    for path in ROOT.rglob('*'):
        if not path.is_file() or any(part in excluded_dirs for part in path.parts):
            continue
        if path.suffix.lower() not in allowed_suffixes:
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        for match in pattern.finditer(text):
            hits.append({'path': str(path.relative_to(ROOT)), 'token_prefix': match.group(0)[:12] + '...'})
    return hits


def run(output_dir='reports/security-monitor'):
    cfg = load(CONFIG)
    current_state = load(CURRENT_STATE)
    report = load(REPORT)
    states = {h['id']: h['estado'] for h in report['hallazgos']}
    security_phase = current_state.get('phases', {}).get('fase_7', {})
    security_phase_status = security_phase.get('status')
    auth = security_phase.get('authentication', {})
    alerts = []

    if security_phase_status != 'MONITOREO_SEGURIDAD_ACTIVO':
        alerts.append('El estado canónico ya no registra el monitoreo de seguridad como activo.')
    if states.get('F7S4-DEFAULT-PRIVILEGES-DATA-API') != 'CORREGIDO_VERIFICADO':
        alerts.append('Regresion documental en Default privileges/Data API.')
    if states.get('F7S4-GALERIA-GRANTS') != 'CORREGIDO_VERIFICADO':
        alerts.append('Regresion documental en grants de Galeria.')
    if states.get('F7S4-AUTH-LEAKED-PASSWORD') != 'ACEPTADO_NO_APLICABLE_EN_PLAN_FREE':
        alerts.append('Cambio no revisado en excepcion de Leaked Password Protection.')

    if auth.get('master') != 'AUTHENTICATED_PLUS_AAL2_MFA':
        alerts.append('El master ya no conserva AAL2/MFA como requisito.')
    if auth.get('mfa_obligatorio_editores') is not False:
        alerts.append('Cambio no autorizado en MFA obligatorio de editores.')

    secret_hits = scan_for_literal_secrets() if cfg['checks']['forbid_literal_sb_secret'] else []
    if secret_hits:
        alerts.append('Se detectaron posibles claves sb_secret_ literales en superficies ejecutables/configurables.')

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    result = {
        'estado': 'ALERTA' if alerts else 'SEGURO',
        'alertas': alerts,
        'state_source': 'state/current.json',
        'security_phase_status': security_phase_status,
        'security_auth_source': security_phase.get('detail_source'),
        'secret_hits': secret_hits,
        'accepted_exceptions': cfg['accepted_exceptions'],
        'live_deep_checks': cfg['live_deep_checks']
    }
    (out / 'resultado.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    lines = [
        '# Monitoreo de seguridad EVA',
        '',
        f"Estado: `{result['estado']}`",
        '',
        f"Fuente de estado: `{result['state_source']}`",
        f"Estado de Fase 7: `{result['security_phase_status']}`",
        f"Detalle de autenticación: `{result['security_auth_source']}`",
        '',
        f"Alertas: {len(alerts)}",
        '',
        '## Excepciones aceptadas',
    ]
    for item in cfg['accepted_exceptions']:
        lines.append(f"- `{item['id']}`: {item['reason']}")
    if alerts:
        lines += ['', '## Alertas'] + [f'- {x}' for x in alerts]
    (out / 'Informe_monitoreo_seguridad.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    result = run(sys.argv[1] if len(sys.argv) > 1 else 'reports/security-monitor')
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(1 if result['alertas'] else 0)
