import json
from pathlib import Path

REPORT = Path("reports/fase-8-etapa-3-linea-base-accesibilidad.json")
GENERATED = Path("reports/fase-8-etapa-3-linea-base-accesibilidad.generated.json")
TRACK = Path("tracking/fase-8-etapa-3.json")
PHASE = Path("tracking/fase-8.json")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    report = load(REPORT)
    track = load(TRACK)
    phase = load(PHASE)

    expected_summary = {"CUMPLE":2,"INCUMPLIMIENTO_CONFIRMADO":0,"REQUIERE_VERIFICACION_CONTROLADA":26,"total":28}
    assert report["estado"] == "ETAPA_3_COMPLETADA_LINEA_BASE_ACCESIBILIDAD"
    assert report["resumen_contratos"] == expected_summary
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

    # El tracking propio de Etapa 3 conserva el snapshot historico de su cierre.
    assert track["estado"] == "ETAPA_3_COMPLETADA_LINEA_BASE_ACCESIBILIDAD"
    assert track["workflow_run_id"] == 37798165287
    assert track["evidencia_pendiente_workflow"] is False
    assert track["etapa_4_iniciada"] is False

    # El tracking vivo de la Fase 8 puede avanzar sin reescribir la linea base.
    assert phase["etapas"][2]["estado"] == "ETAPA_3_COMPLETADA_LINEA_BASE_ACCESIBILIDAD"
    assert phase["etapa_3"]["estado"] == "ETAPA_3_COMPLETADA_LINEA_BASE_ACCESIBILIDAD"
    assert phase["etapa_3"]["resultado"]["incumplimientos_confirmados"] == 0
    assert isinstance(phase["etapa_3"]["etapa_4_iniciada"], bool)
    if phase["etapa_3"]["etapa_4_iniciada"]:
        assert phase.get("etapa_4_iniciada") is True
        assert "etapa_4" in phase

    # En Etapa 3 no se modifico EVA. Si la fase ya avanzo a Etapa 7, es legitimo
    # que el tracking vivo registre cambios por la correccion controlada posterior.
    if phase.get("etapa_7_iniciada"):
        assert phase["repositorios_eva_modificados"] is True
        assert phase["etapa_7"]["estado"] == "ETAPA_7_COMPLETADA_CORRECCION_CONTROLADA_ACCESIBILIDAD"
    else:
        assert phase["repositorios_eva_modificados"] is False

    if GENERATED.exists():
        generated = load(GENERATED)
        assert generated["resumen_contratos"] == expected_summary
        assert generated["universo"]["repositorios"] == 8
        assert generated["universo"]["paginas_html_referencia_etapa_1"] == 65
        assert generated["universo"]["paginas_html_observadas_actualmente"] == 66
        assert generated["metricas_estaticas"]["form_controls_missing_label"] == 1
        assert generated["metricas_estaticas"]["images_missing_alt"] == 0
        assert generated["metricas_estaticas"]["controls_missing_name"] == 0

    print("Validacion Fase 8 Etapa 3: OK")


if __name__ == "__main__":
    main()
