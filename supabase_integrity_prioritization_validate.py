import json
from pathlib import Path

REPORT = Path('reports/fase-6-etapa-4-priorizacion.json')


def validate(data: dict) -> None:
    assert data['fase'] == 6 and data['etapa'] == 4
    assert data['estado'] == 'ETAPA_4_COMPLETADA_PRIORIZACION_INTEGRIDAD'
    r = data['resumen']
    assert r['contratos_auditados'] == 42
    assert r['inconsistencias_confirmadas'] == 0
    assert r['hallazgos_prioritarios'] == 0
    assert data['hallazgos_priorizados'] == []
    assert sum(r[k] for k in ('P0_CRITICA','P1_ALTA','P2_MEDIA','P3_BAJA')) == 0
    assert r['storage_candidatos_revision'] == 24
    assert r['supabase_modificado'] is False
    assert r['repositorios_eva_modificados'] is False
    ids = {x['id'] for x in data['observaciones_no_hallazgo']}
    assert {'STORAGE-CANDIDATOS-REVISION','SEC-DEPENDENCY-001'} <= ids
    assert data['politica']['no_inventar_hallazgos'] is True
    assert data['politica']['storage_no_referenciado_no_se_elimina'] is True


if __name__ == '__main__':
    validate(json.loads(REPORT.read_text(encoding='utf-8')))
    print('OK: priorizacion de integridad validada')
