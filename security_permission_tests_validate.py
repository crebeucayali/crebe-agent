import json
from pathlib import Path

REPORT = Path('reports/fase-7-etapa-5-pruebas-permisos.json')
REQUIRED = {'SEC-CON-007','SEC-CON-012','SEC-CON-013','SEC-CON-015','SEC-CON-023'}


def validate(path=REPORT):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    assert data['fase'] == 7 and data['etapa'] == 5
    assert data['estado'] == 'ETAPA_5_COMPLETADA_PRUEBAS_PERMISOS'
    assert data['modo'] == 'CONTROLLED_PERMISSION_TESTS_ROLLBACK'
    assert set(data['contratos_probados']) == REQUIRED
    result = data['resultado']
    assert result == {'contratos_probados': 5, 'aprobados': 5, 'fallidos': 0, 'residuos': 0}
    pruebas = {p['id']: p for p in data['pruebas']}
    assert set(pruebas) == REQUIRED
    assert all(p['resultado'] == 'PASS' and p['persistencia'] is False for p in pruebas.values())
    g = data['guardrails']
    assert all(g.values())
    assert len(data['hallazgos_priorizados_etapa_4_sin_corregir']) == 3
    assert data['correccion_autorizada'] is False
    assert data['etapa_6_iniciada'] is False
    return True


if __name__ == '__main__':
    validate()
    print('Fase 7 Etapa 5 evidence: OK')
