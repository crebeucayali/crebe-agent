import json
import sys
from pathlib import Path

REPORT = Path('reports/fase-8-etapa-6-diagnostico-accesibilidad.json')
TRACK = Path('tracking/fase-8-etapa-6.json')
PHASE = Path('tracking/fase-8.json')
GENERATED = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('reports/fase-8-etapa-6-diagnostico.generated.json')


def load(p):
    return json.loads(p.read_text(encoding='utf-8'))


def main():
    report = load(REPORT)
    track = load(TRACK)
    phase = load(PHASE)

    # La Etapa 6 permanece como evidencia historica previa a la correccion.
    assert report['estado'] == 'ETAPA_6_COMPLETADA_DIAGNOSTICO_ACCESIBILIDAD'
    assert report['resumen']['nodos_contraste_confirmados'] == 77
    assert report['resumen']['grupos_causales_contraste'] == 6
    assert report['resumen']['urls_overflow_320'] == 4
    assert report['resumen']['grupos_causales_overflow'] == 3
    assert report['resumen']['grupos_causales_totales'] == 9
    assert report['resumen']['correcciones_aplicadas'] == 0
    assert report['guardrails']['repositorios_eva_modificados'] is False
    assert report['guardrails']['supabase_modificado'] is False
    assert len(report['diagnostico_contraste']) == 6
    assert sum(x['nodos'] for x in report['diagnostico_contraste']) == 77
    assert len(report['diagnostico_reflujo']) == 3
    assert track['estado'] == 'ETAPA_6_COMPLETADA_DIAGNOSTICO_ACCESIBILIDAD'
    assert track['resultado']['grupos_causales_totales'] == 9
    assert phase['etapas'][5]['estado'] == 'ETAPA_6_COMPLETADA_DIAGNOSTICO_ACCESIBILIDAD'
    assert phase['etapa_6']['resultado']['grupos_causales_totales'] == 9

    etapa_7_iniciada = bool(phase.get('etapa_7_iniciada', phase['etapa_6'].get('etapa_7_iniciada', False)))
    if etapa_7_iniciada:
        assert phase['etapa_6']['etapa_7_iniciada'] is True
        assert 'etapa_7' in phase
    else:
        assert report['guardrails']['etapa_7_iniciada'] is False
        assert track['etapa_7_iniciada'] is False
        assert phase['etapa_6']['etapa_7_iniciada'] is False
        assert phase['repositorios_eva_modificados'] is False

    if GENERATED.exists():
        generated = load(GENERATED)
        assert generated['guardrails']['repositorios_eva_modificados'] is False
        assert generated['guardrails']['supabase_modificado'] is False
        if etapa_7_iniciada:
            # Verificacion real post-correccion: ninguna de las causas objetivo debe persistir.
            assert generated['contraste']['nodos'] == 0
            assert len(generated['reflujo']['detalle']) == 0
        else:
            assert generated['contraste']['nodos'] == 77
            assert len(generated['reflujo']['detalle']) == 4

    print('Validacion Fase 8 Etapa 6 / progresion Etapa 7: OK')


if __name__ == '__main__':
    main()
