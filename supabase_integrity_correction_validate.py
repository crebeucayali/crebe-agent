import json
from pathlib import Path

REPORT = Path('reports/fase-6-etapa-7-correccion-controlada.json')
TRACKING = Path('tracking/fase-6-etapa-7.json')


def validate():
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    tracking = json.loads(TRACKING.read_text(encoding='utf-8'))
    assert report['estado'] == 'ETAPA_7_COMPLETADA_CORRECCION_CONTROLADA'
    assert report['modo'] == 'NO_INTERVENTION_REQUIRED'
    r = report['resultado']
    assert r['hallazgos_que_requieren_correccion'] == 0
    assert r['intervenciones_ejecutadas'] == 0
    assert r['migraciones_ejecutadas'] == 0
    assert r['cambios_rls_grants'] == 0
    assert r['objetos_storage_eliminados'] == 0
    assert r['supabase_modificado'] is False
    assert r['repositorios_eva_modificados'] is False
    assert tracking['criterios_cierre_cumplidos'] is True
    assert tracking['etapa_8_iniciada'] is False
    print('ETAPA_7_VALIDADA')


if __name__ == '__main__':
    validate()
