import json
from pathlib import Path


def load_report():
    return json.loads(Path('reports/fase-6-etapa-7-correccion-controlada.json').read_text(encoding='utf-8'))


def test_no_intervention_required():
    report = load_report()
    assert report['modo'] == 'NO_INTERVENTION_REQUIRED'
    assert report['resultado']['hallazgos_que_requieren_correccion'] == 0
    assert report['resultado']['intervenciones_ejecutadas'] == 0


def test_production_unchanged():
    result = load_report()['resultado']
    assert result['supabase_modificado'] is False
    assert result['repositorios_eva_modificados'] is False
    assert result['objetos_storage_eliminados'] == 0


def test_deferred_items_preserved():
    result = load_report()['resultado']
    assert result['storage_candidatos_revision_conservados'] == 24
    assert result['dependencias_seguridad_conservadas'] == 1
