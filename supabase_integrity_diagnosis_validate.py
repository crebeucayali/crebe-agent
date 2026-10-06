import json
from pathlib import Path

REPORT = Path("reports/fase-6-etapa-6-diagnostico.json")


def validate(data):
    assert data["fase"] == 6
    assert data["etapa"] == 6
    assert data["estado"] == "ETAPA_6_COMPLETADA_DIAGNOSTICO_INTEGRIDAD"
    result = data["resultado"]
    assert result["inconsistencias_confirmadas"] == 0
    assert result["hallazgos_diagnosticables"] == 0
    assert result["hallazgos_que_requieren_correccion"] == 0
    assert result["storage_candidatos_revision"] == 24
    assert result["dependencias_seguridad"] == 1
    assert result["correccion_autorizada"] is False
    assert result["supabase_modificado"] is False
    assert result["repositorios_eva_modificados"] is False
    assert data["etapa_7_requerida_por_hallazgos_actuales"] is False
    ids = {x["id"] for x in data["separaciones"]}
    assert ids == {"STORAGE-CANDIDATES-001", "SEC-DEPENDENCY-001"}
    return True


def main():
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    validate(data)
    print("Fase 6 Etapa 6: diagnostico validado")


if __name__ == "__main__":
    main()
