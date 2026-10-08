import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / 'reports' / 'fase-8-etapa-2-contratos-accesibilidad.json'
TRACKING = ROOT / 'tracking' / 'fase-8-etapa-2.json'
SCOPE = ROOT / 'config' / 'fase-8-accessibility-scope.json'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def validate():
    report = load(REPORT)
    tracking = load(TRACKING)
    scope = load(SCOPE)

    assert report['fase'] == 8 and report['etapa'] == 2
    assert report['estado'] == 'ETAPA_2_COMPLETADA_CONTRATOS_ACCESIBILIDAD'
    assert report['modo'] == 'READ_ONLY_CONTRACT_DEFINITION'
    assert report['referencia_tecnica']['estandar'] == 'WCAG 2.2'
    assert report['referencia_tecnica']['nivel_objetivo'] == 'AA'
    assert report['superficies_cubiertas'] == len(scope['superficies']) == 14
    assert report['contratos_totales'] == len(report['contratos']) == 28

    ids = [x['id'] for x in report['contratos']]
    assert len(ids) == len(set(ids)) == 28
    assert all(x['superficie'] in scope['superficies'] for x in report['contratos'])

    counts = {surface: 0 for surface in scope['superficies']}
    for contract in report['contratos']:
        counts[contract['superficie']] += 1
    assert all(value == 2 for value in counts.values())

    assert report['hallazgos_confirmados'] == 0
    assert report['severidades_asignadas'] == 0
    assert report['correcciones_aplicadas'] == 0
    assert report['repositorios_eva_modificados'] is False
    assert report['guardrails']['no_declarar_conformidad_wcag'] is True
    assert report['guardrails']['no_declarar_fallos_sin_evidencia'] is True
    assert report['guardrails']['no_asignar_severidad_en_etapa_2'] is True
    assert report['guardrails']['no_aplicar_correcciones_en_etapa_2'] is True
    assert report['guardrails']['etapa_3_no_iniciada'] is True

    assert tracking['estado'] == 'ETAPA_2_COMPLETADA_CONTRATOS_ACCESIBILIDAD'
    assert tracking['resultado']['contratos_definidos'] == 28
    assert tracking['resultado']['repositorios_eva_modificados'] is False
    assert tracking['criterios_cierre_cumplidos'] is True
    assert tracking['etapa_3_iniciada'] is False

    print(json.dumps({
        'estado': 'OK',
        'superficies': 14,
        'contratos': 28,
        'hallazgos_confirmados': 0,
        'severidades_asignadas': 0,
        'repositorios_eva_modificados': False,
        'etapa_3_iniciada': False
    }, ensure_ascii=False))


if __name__ == '__main__':
    validate()
