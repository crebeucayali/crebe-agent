import json
from pathlib import Path

REPORT = Path('reports/fase-7-etapa-7-correccion-seguridad.json')


def validate(path=REPORT):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    assert data['fase'] == 7 and data['etapa'] == 7
    assert data['estado'] == 'ETAPA_7_COMPLETADA_CORRECCION_SEGURIDAD'
    r = data['resultado']
    assert r['hallazgos_objetivo'] == 3
    assert r['corregidos_verificados'] == 2
    assert r['aceptados_no_aplicables_plan_free'] == 1
    assert r['parcialmente_corregidos'] == 0
    assert r['bloqueados'] == 0
    assert r['supabase_modificado'] is True
    assert r['repositorios_eva_modificados'] is False
    assert r['rls_modificado'] is False
    assert r['etapa_8_iniciada'] is False
    estados = {h['id']: h['estado'] for h in data['hallazgos']}
    assert estados['F7S4-GALERIA-GRANTS'] == 'CORREGIDO_VERIFICADO'
    assert estados['F7S4-DEFAULT-PRIVILEGES-DATA-API'] == 'CORREGIDO_VERIFICADO'
    assert estados['F7S4-AUTH-LEAKED-PASSWORD'] == 'ACEPTADO_NO_APLICABLE_EN_PLAN_FREE'
    leaked = next(h for h in data['hallazgos'] if h['id'] == 'F7S4-AUTH-LEAKED-PASSWORD')
    assert leaked['decision_usuario'] == 'MANTENER_PLAN_FREE'
    assert leaked['cambio_aplicado'] is False
    assert data['guardrails']['no_relajar_rls'] is True
    assert data['guardrails']['no_imponer_mfa_editores_sin_decision_separada'] is True
    return True


if __name__ == '__main__':
    validate()
    print('OK')
