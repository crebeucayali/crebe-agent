import json
from pathlib import Path

REPORT = Path("reports/fase-8-etapa-4-priorizacion-accesibilidad.json")
TRACK = Path("tracking/fase-8-etapa-4.json")
PHASE = Path("tracking/fase-8.json")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    report = load(REPORT)
    track = load(TRACK)
    phase = load(PHASE)

    assert report["estado"] == "ETAPA_4_COMPLETADA_PRIORIZACION_ACCESIBILIDAD"
    assert report["contratos_totales"] == 28
    assert report["cumple_estructural"] == 2
    assert report["incumplimientos_confirmados"] == 0
    assert report["requiere_verificacion_controlada"] == 26
    assert report["prioridades_verificacion"] == {"P0": 11, "P1": 13, "P2": 2}

    groups = report["grupos"]
    assert len(groups) == 3
    all_contracts = [c for group in groups for c in group["contratos"]]
    assert len(all_contracts) == 26
    assert len(set(all_contracts)) == 26
    assert "A11Y-CON-001" not in all_contracts
    assert "A11Y-CON-003" not in all_contracts
    assert report["severidades_de_fallos_asignadas"] == 0
    assert report["hallazgos_confirmados_nuevos"] == 0
    assert report["correcciones_aplicadas"] == 0
    assert report["repositorios_eva_modificados"] is False
    assert report["supabase_modificado"] is False
    assert report["etapa_5_iniciada"] is False

    # El snapshot propio de Etapa 4 conserva el estado historico de su cierre.
    assert track["estado"] == "ETAPA_4_COMPLETADA_PRIORIZACION_ACCESIBILIDAD"
    assert track["resultado"]["prioridad_p0"] == 11
    assert track["resultado"]["prioridad_p1"] == 13
    assert track["resultado"]["prioridad_p2"] == 2
    assert track["etapa_5_iniciada"] is False

    # El tracking vivo puede progresar a etapas posteriores sin reescribir Etapa 4.
    assert phase["etapas"][3]["estado"] == "ETAPA_4_COMPLETADA_PRIORIZACION_ACCESIBILIDAD"
    assert phase["etapa_4"]["resultado"]["requiere_verificacion_controlada"] == 26
    assert isinstance(phase["etapa_4"]["etapa_5_iniciada"], bool)
    if phase["etapa_4"]["etapa_5_iniciada"]:
        assert phase.get("etapa_5_iniciada") is True
        assert "etapa_5" in phase

    # Antes de la correccion, EVA seguia intacto; tras Etapa 7 es legitimo que el
    # tracking vivo registre los repositorios modificados por la correccion controlada.
    if phase.get("etapa_7_iniciada"):
        assert phase["repositorios_eva_modificados"] is True
        assert phase["etapa_7"]["estado"] == "ETAPA_7_COMPLETADA_CORRECCION_CONTROLADA_ACCESIBILIDAD"
    else:
        assert phase["repositorios_eva_modificados"] is False

    print("Validacion Fase 8 Etapa 4: OK")


if __name__ == "__main__":
    main()
