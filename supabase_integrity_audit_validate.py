import json
from pathlib import Path

ALLOWED = {
    'INTEGRO',
    'INCONSISTENCIA_CONFIRMADA',
    'REQUIERE_VERIFICACION_CONTROLADA',
    'BLOQUEADO_POR_PERMISOS_O_DEPENDENCIA',
    'NO_APLICA',
}

ROOT = Path(__file__).resolve().parent
CONTRACTS = ROOT / 'contracts' / 'fase-6-etapa-2-integridad.json'
REPORT = ROOT / 'reports' / 'fase-6-etapa-3-integridad.json'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def contract_ids(data):
    ids = [r['id'] for r in data['reglas_globales']]
    for module in data['modulos']:
        ids.extend(c['id'] for c in module['contratos'])
    return ids


def validate():
    contracts = load(CONTRACTS)
    report = load(REPORT)
    expected = contract_ids(contracts)
    results = report['resultados']
    actual = [r['id'] for r in results]

    assert len(expected) == 42, f'Expected 42 contracts, got {len(expected)}'
    assert len(actual) == len(set(actual)), 'Duplicate result IDs'
    assert set(actual) == set(expected), 'Audit results do not cover exactly the contract IDs'
    assert all(r['estado'] in ALLOWED for r in results), 'Invalid audit state'
    assert all(str(r.get('evidencia', '')).strip() for r in results), 'Every result needs evidence'

    summary = report['resumen']
    counts = {state: sum(r['estado'] == state for r in results) for state in ALLOWED}
    assert summary['contratos_totales'] == 42
    for state, value in counts.items():
        assert summary[state] == value, f'Summary mismatch for {state}'
    assert summary['hallazgos_confirmados'] == counts['INCONSISTENCIA_CONFIRMADA']
    assert summary['supabase_modificado'] is False
    assert summary['repositorios_eva_modificados'] is False

    storage = report['evidencia_clave']['storage']
    assert storage['referencias_faltantes'] == 0
    assert storage['objetos_no_referenciados_candidatos_revision'] >= 0
    assert contracts['escritura_habilitada'] is False
    assert contracts['correccion_automatica'] is False
    return True


if __name__ == '__main__':
    validate()
    print('Fase 6 Etapa 3: auditoria de integridad validada')
