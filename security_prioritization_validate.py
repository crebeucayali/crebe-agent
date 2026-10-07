import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "reports/fase-7-etapa-4-priorizacion-seguridad.json"


def validate(data=None):
    d = data or json.loads(REPORT.read_text(encoding="utf-8"))
    assert d["estado"] == "ETAPA_4_COMPLETADA_PRIORIZACION_SEGURIDAD"
    assert d["modo"] == "READ_ONLY_CLASSIFICATION"
    assert d["contratos_incumplidos"] == 5
    assert d["hallazgos_causales"] == 3
    assert d["severidad"] == {"CRITICO": 0, "ALTO": 1, "MEDIO": 2, "BAJO": 0}
    ids = [x["id"] for x in d["hallazgos"]]
    assert len(ids) == len(set(ids)) == 3
    mapped = [c for h in d["hallazgos"] for c in h["contratos"]]
    assert set(mapped) == {"SEC-CON-001", "SEC-CON-003", "SEC-CON-004", "SEC-CON-011", "SEC-CON-026"}
    assert d["pendientes_prueba_controlada"] == ["SEC-CON-007", "SEC-CON-012", "SEC-CON-013", "SEC-CON-015", "SEC-CON-023"]
    assert d["correcciones_autorizadas"] == 0
    assert d["supabase_modificado"] is False
    assert d["repositorios_eva_modificados"] is False
    return True


if __name__ == "__main__":
    validate()
    print("phase 7 stage 4 prioritization: OK")
