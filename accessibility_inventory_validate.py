import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / 'reports/fase-8-etapa-1-inventario-accesibilidad.json'
TRACKING = ROOT / 'tracking/fase-8-etapa-1.json'
SCOPE = ROOT / 'config/fase-8-accessibility-scope.json'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def validate():
    report = load(REPORT)
    tracking = load(TRACKING)
    scope = load(SCOPE)

    assert report['fase'] == 8 and report['etapa'] == 1
    assert report['estado'] == 'ETAPA_1_COMPLETADA_INVENTARIO_ACCESIBILIDAD'
    assert report['modo'] == 'READ_ONLY'
    assert report['universo']['repositorios'] == 8
    assert report['universo']['paginas_html'] == 65
    assert report['universo']['elementos_funcionales'] == 1297
    assert report['superficies_inventariadas'] == 14
    assert len(report['superficies']) == 14
    assert report['hallazgos_confirmados'] == 0
    assert report['severidades_asignadas'] == 0
    assert report['correcciones_autorizadas'] == 0
    assert report['repositorios_eva_modificados'] is False

    ids = [item['id'] for item in report['superficies']]
    assert len(ids) == len(set(ids)) == 14
    assert scope['reglas']['no_corregir_en_etapa_1'] is True
    assert scope['reglas']['no_declarar_defectos_sin_evidencia'] is True
    assert len(scope['repositorios']) == 8

    assert tracking['estado'] == 'ETAPA_1_COMPLETADA_INVENTARIO_ACCESIBILIDAD'
    assert tracking['criterios_cierre_cumplidos'] is True
    assert tracking['repositorios_eva_modificados'] is False
    assert tracking['etapa_2_iniciada'] is False

    print(json.dumps({
        'estado': 'OK',
        'repositorios': 8,
        'paginas_html': 65,
        'elementos_funcionales': 1297,
        'superficies_inventariadas': 14,
        'hallazgos_confirmados': 0,
        'repositorios_eva_modificados': False,
        'etapa_2_iniciada': False
    }, ensure_ascii=False))


if __name__ == '__main__':
    validate()
