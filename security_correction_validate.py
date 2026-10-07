import json
from pathlib import Path

REPORT = Path('reports/fase-7-etapa-7-correccion-seguridad.json')


def validate(path=REPORT):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    assert data['fase'] == 7 and data['etapa'] == 7
    assert data['estado'] == 'ETAPA_7_EN_CURSO_CON_BLOQUEOS_CONTROLADOS'
    r = data['resultado']
    assert r['hallazgos_objetivo'] == 3
    assert r['corregidos_verificados'] == 1
    assert r['parcialmente_corregidos'] == 1
    assert r.get('bloqueados_por_capacidad_o_plan', r.get('bloqueados_por_capacidad_plataforma')) == 1
    assert r['supabase_modificado'] is True
    assert r['repositorios_eva_modificados'] is False
    assert r['rls_modificado'] is False
    assert r['etapa_8_iniciada'] is False
    estados = {h['id']: h['estado'] for h in data['hallazgos']}
    assert estados['F7S4-GALERIA-GRANTS'] == 'CORREGIDO_VERIFICADO'
    assert estados['F7S4-DEFAULT-PRIVILEGES-DATA-API'] == 'PARCIALMENTE_CORREGIDO'
    assert estados['F7S4-AUTH-LEAKED-PASSWORD'] in {'BLOQUEADO_POR_CAPACIDAD_HERRAMIENTA', 'BLOQUEADO_POR_PLAN'}
    assert data['guardrails']['no_relajar_rls'] is True
    assert data['guardrails']['no_iniciar_etapa_8_hasta_resolver_bloqueos'] is True
    return True


if __name__ == '__main__':
    validate()
    print('OK')
