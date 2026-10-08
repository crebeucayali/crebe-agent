import json
from pathlib import Path

REPORT = Path("reports/fase-8-etapa-3-linea-base-accesibilidad.json")
TRACK = Path("tracking/fase-8-etapa-3.json")
PHASE = Path("tracking/fase-8.json")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    report = load(REPORT)
    track = load(TRACK)
    phase = load(PHASE)

    assert report["estado"] == "ETAPA_3_COMPLETADA_LINEA_BASE_ACCESIBILIDAD"
    assert report["resumen_contratos"] == {
        "CUMPLE": 2,
        "INCUMPLIMIENTO_CONFIRMADO": 0,
        "REQUIERE_VERIFICACION_CONTROLADA": 26,
        "total": 28,
    }
    assert report["universo"]["repositorios"] == 8
    assert report["universo"]["paginas_html_referencia_etapa_1"] == 65
    assert report["universo"]["paginas_html_observadas_actualmente"] == 66
    assert report["metricas_estaticas"]["candidatos_control_formulario_sin_etiqueta_estatica"] == 1
    assert report["guardrails"]["repositorios_eva_modificados"] is False
    assert report["guardrails"]["supabase_modificado"] is False
    assert report["guardrails"]["correcciones_aplicadas"] == 0
    assert report["guardrails"]["severidades_asignadas"] == 0
    assert report["guardrails"]["priorizacion_realizada"] is False
    assert report["guardrails"]["etapa_4_iniciada"] is False

    assert track["estado"] == "ETAPA_3_COMPLETADA_LINEA_BASE_ACCESIBILIDAD"
    assert track["workflow_run_id"] == 37798165287
    assert track["evidencia_pendiente_workflow"] is False
    assert track["etapa_4_iniciada"] is False

    assert phase["etapas"][2]["estado"] == "ETAPA_3_COMPLETADA_LINEA_BASE_ACCESIBILIDAD"
    assert phase["etapa_3"]["estado"] == "ETAPA_3_COMPLETADA_LINEA_BASE_ACCESIBILIDAD"
    assert phase["etapa_3"]["resultado"]["incumplimientos_confirmados"] == 0
    assert phase["etapa_3"]["etapa_4_iniciada"] is False
    assert phase["repositorios_eva_modificados"] is False

    print("Validacion Fase 8 Etapa 3: OK")


if __name__ == "__main__":
    main()
