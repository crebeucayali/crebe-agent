import json
from pathlib import Path

REPORT = Path('reports/fase-7-etapa-6-diagnostico-seguridad.json')


def validate(path=REPORT):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    assert data['estado'] == 'ETAPA_6_COMPLETADA_DIAGNOSTICO_SEGURIDAD'
    assert data['modo'] == 'READ_ONLY_DIAGNOSIS'
    assert data['hallazgos_diagnosticados'] == 3
    assert data['correcciones_autorizadas'] == 0
    assert data['supabase_modificado'] is False
    assert data['repositorios_eva_modificados'] is False
    assert data['etapa_7_iniciada'] is False
    ids = [x['id'] for x in data['hallazgos']]
    assert ids == [
        'F7S4-DEFAULT-PRIVILEGES-DATA-API',
        'F7S4-GALERIA-GRANTS',
        'F7S4-AUTH-LEAKED-PASSWORD',
    ]
    assert [x['prioridad'] for x in data['hallazgos']] == ['ALTO', 'MEDIO', 'MEDIO']
    assert all(x['listo_para_correccion_controlada'] for x in data['hallazgos'])
    assert data['pruebas_etapa_5']['contratos_aprobados'] == 5
    assert data['pruebas_etapa_5']['hallazgos_nuevos'] == 0
    assert data['pruebas_etapa_5']['residuos'] == 0
    assert data['fecha_limite_data_api'] == '2026-10-30'
    return True


if __name__ == '__main__':
    validate()
    print('ETAPA_6_DIAGNOSTICO_SEGURIDAD_VALIDO')
