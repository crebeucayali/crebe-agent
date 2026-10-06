import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / 'reports' / 'fase-7-etapa-1-inventario-seguridad.json'
TRACKING = ROOT / 'tracking' / 'fase-7-etapa-1.json'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def validate():
    report = load(REPORT)
    tracking = load(TRACKING)

    assert report['fase'] == 7 and report['etapa'] == 1
    assert report['estado'] == 'ETAPA_1_COMPLETADA_INVENTARIO_SEGURIDAD'
    assert report['modo'] == 'READ_ONLY'
    assert report['supabase']['objetos_catalogados'] == 21
    assert report['supabase']['politicas_rls_catalogadas'] == 36
    assert report['supabase']['funciones_publicas_security_definer'] == 0
    assert report['supabase']['funciones_private_catalogadas'] == 24
    assert report['supabase']['funciones_private_security_definer'] == 19
    assert report['supabase']['vista_publica']['security_invoker'] is True
    assert report['github']['service_role_literal_detectado'] is False
    assert report['github']['sb_secret_literal_detectado'] is False
    assert report['reglas_de_inventario']['no_secret_values_in_report'] is True
    assert report['reglas_de_inventario']['no_risk_severity_assigned_yet'] is True
    assert report['reglas_de_inventario']['no_corrections_authorized'] is True
    assert report['reglas_de_inventario']['supabase_modified'] is False
    assert report['reglas_de_inventario']['eva_repositories_modified'] is False

    surface_ids = [item['id'] for item in report['superficies_a_contratar_en_etapa_2']]
    assert len(surface_ids) == len(set(surface_ids)) == 6
    assert 'SEC-SURFACE-001' in surface_ids
    assert 'SEC-SURFACE-002' in surface_ids

    assert tracking['estado'] == 'ETAPA_1_COMPLETADA_INVENTARIO_SEGURIDAD'
    assert tracking['criterios_cierre_cumplidos'] is True
    assert tracking['etapa_2_iniciada'] is False
    assert tracking['supabase_modificado'] is False
    assert tracking['repositorios_eva_modificados'] is False

    print(json.dumps({
        'estado': 'OK',
        'objetos_catalogados': report['supabase']['objetos_catalogados'],
        'politicas_rls': report['supabase']['politicas_rls_catalogadas'],
        'superficies_inventariadas': len(surface_ids),
        'secretos_privados_literales_detectados': 0,
        'supabase_modificado': False,
        'repositorios_eva_modificados': False,
    }, ensure_ascii=False))


if __name__ == '__main__':
    validate()
