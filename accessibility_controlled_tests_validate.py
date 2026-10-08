import json
import sys
from pathlib import Path

REPORT = Path("reports/fase-8-etapa-5-pruebas-controladas.json")
TRACK = Path("tracking/fase-8-etapa-5.json")
PHASE = Path("tracking/fase-8.json")
PHASES = Path("tracking/phases.json")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Uso: accessibility_controlled_tests_validate.py <evidencia-generada.json>")

    generated = load(Path(sys.argv[1]))
    report = load(REPORT)
    track = load(TRACK)
    phase = load(PHASE)
    phases = load(PHASES)

    expected_state = "ETAPA_5_COMPLETADA_PRUEBAS_CONTROLADAS_ACCESIBILIDAD"
    assert report["estado"] == expected_state
    assert track["estado"] == expected_state
    assert phase["etapas"][4]["estado"] == expected_state
    assert phase["etapa_5"]["estado"] == expected_state
    assert phases["fase_8"]["etapa_5_estado"] == expected_state

    # La evidencia histórica que cerró Etapa 5 es inmutable.
    assert report["workflow_run_id"] == 37803532344
    assert report["artifact_id"] == 11561852492
    assert track["workflow_run_id"] == 37803532344
    assert track["artifact_id"] == 11561852492
    historical_summary = {
        "REQUIERE_DIAGNOSTICO_O_REVISION_MANUAL": 22,
        "INCUMPLIMIENTO_CONFIRMADO_AUTOMATIZADO": 1,
        "EVIDENCIA_FAVORABLE_CONTROLADA": 1,
        "REQUIERE_DIAGNOSTICO": 1,
        "NO_APLICA_EN_UNIVERSO_OBSERVADO": 1,
    }
    assert sum(historical_summary.values()) == 26
    for key, value in historical_summary.items():
        assert report["resumen_contratos_pendientes"][key] == value
    assert report["resumen_contratos_pendientes"]["total"] == 26

    # El workflow puede volver a ejecutarse en etapas posteriores sobre el EVA actual.
    # Se valida el mismo universo y los guardrails, pero no se exige reproducir fallos
    # que Etapas 6-7 ya diagnosticaron y corrigieron.
    assert generated["fase"] == 8 and generated["etapa"] == 5
    assert generated["paginas_observadas"] == report["universo"]["paginas_html_observadas"] == 66
    assert generated["paginas_funcionales_completamente_probadas"] == report["universo"]["paginas_funcionales_completamente_probadas"] == 63
    assert generated["paginas_funcionales_incompletas"] == report["universo"]["paginas_funcionales_incompletas"] == 0
    assert generated["paginas_auxiliares"] == report["universo"]["paginas_auxiliares"] == 3
    assert generated["paginas_no_cargadas"] == report["universo"]["paginas_no_cargadas"] == 0
    assert generated["tablas_observadas"] == report["universo"]["tablas_observadas"] == 22
    assert generated["multimedia_observada"] == report["universo"]["multimedia_observada"] == 0
    assert sum(generated["resumen_estados"].values()) == 26

    stage7_completed = phase.get("etapa_7", {}).get("estado") == "ETAPA_7_COMPLETADA_CORRECCION_CONTROLADA_ACCESIBILIDAD"
    if stage7_completed:
        verification = phase["etapa_7"].get("verificacion_post_correccion", {})
        assert verification.get("nodos_contraste") == 0
        assert verification.get("fallos_overflow_320") == 0
        # Tras la corrección ya no debe reaparecer en la lectura actual la clasificación
        # de fallo automatizado/diagnóstico que motivó Etapas 6-7.
        assert generated["resumen_estados"].get("INCUMPLIMIENTO_CONFIRMADO_AUTOMATIZADO", 0) == 0
        assert generated["resumen_estados"].get("REQUIERE_DIAGNOSTICO", 0) == 0
    else:
        # Antes de la corrección, una reejecución de Etapa 5 debe reproducir su cierre.
        assert generated["resumen_estados"] == historical_summary
        contracts = generated["contratos"]
        assert contracts["A11Y-CON-013"]["status"] == "EVIDENCIA_FAVORABLE_CONTROLADA"
        assert contracts["A11Y-CON-013"]["pagesWithFocusable"] == 63
        assert contracts["A11Y-CON-013"]["pagesFirstTabWithoutFocus"] == 0
        assert contracts["A11Y-CON-023"]["status"] == "INCUMPLIMIENTO_CONFIRMADO_AUTOMATIZADO"
        assert contracts["A11Y-CON-023"]["axeViolations"] == 77
        assert contracts["A11Y-CON-025"]["status"] == "REQUIERE_DIAGNOSTICO"
        assert contracts["A11Y-CON-025"]["pagesWithHorizontalOverflowAt320"] == 4

    assert generated["contratos"]["A11Y-CON-027"]["status"] == "NO_APLICA_EN_UNIVERSO_OBSERVADO"

    for obj in (report["guardrails"], generated["guardrails"]):
        assert obj["repositorios_eva_modificados"] is False
        assert obj["supabase_modificado"] is False
        assert obj["correcciones_aplicadas"] == 0
        assert obj["severidades_asignadas"] == 0

    # El cierre histórico de Etapa 5 permanece inmutable, pero el tracking global
    # puede avanzar legítimamente a Etapa 6 o posteriores.
    assert report["guardrails"]["etapa_6_iniciada"] is False
    assert track["etapa_6_iniciada"] is False
    assert isinstance(phase["etapa_5"]["etapa_6_iniciada"], bool)
    if phase["etapa_5"]["etapa_6_iniciada"]:
        assert phase.get("etapa_6_iniciada") is True
        assert "etapa_6" in phase
    assert isinstance(phases["fase_8"]["etapa_6_iniciada"], bool)
    if phases["fase_8"]["etapa_6_iniciada"]:
        assert phases["fase_8"]["etapa_actual"] >= 6
        assert phases["fase_8"].get("etapa_6_estado") == "ETAPA_6_COMPLETADA_DIAGNOSTICO_ACCESIBILIDAD"

    print("Validacion Fase 8 Etapa 5: OK (evidencia historica preservada; progreso posterior permitido)")


if __name__ == "__main__":
    main()
