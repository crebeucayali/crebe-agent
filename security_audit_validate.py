from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "reports" / "fase-7-etapa-3-linea-base-seguridad.json"
CONTRACTS = ROOT / "contracts" / "fase-7-etapa-2-contratos-seguridad.json"
TRACKING = ROOT / "tracking" / "fase-7-etapa-3.json"

ALLOWED = {"CUMPLE","INCUMPLIMIENTO_CONFIRMADO","REQUIERE_PRUEBA_CONTROLADA","REQUIERE_REVISION_MANUAL","NO_APLICA"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate() -> list[str]:
    errors: list[str] = []
    if not REPORT.exists() or not CONTRACTS.exists() or not TRACKING.exists():
        return ["Faltan artefactos obligatorios de Etapa 3"]
    report = load(REPORT)
    contracts = load(CONTRACTS)
    tracking = load(TRACKING)
    if report.get("estado") != "ETAPA_3_COMPLETADA_LINEA_BASE_SEGURIDAD":
        errors.append("Estado de reporte invalido")
    if report.get("modo") != "READ_ONLY":
        errors.append("La auditoria debe permanecer READ_ONLY")
    contract_ids = {c["id"] for c in contracts.get("contratos", [])}
    results = report.get("resultados", [])
    result_ids = [r.get("id") for r in results]
    if len(result_ids) != 26 or set(result_ids) != contract_ids:
        errors.append("Los 26 contratos deben estar auditados exactamente una vez")
    if len(result_ids) != len(set(result_ids)):
        errors.append("Hay contratos duplicados en la linea base")
    if any(r.get("estado") not in ALLOWED for r in results):
        errors.append("Existe un estado de auditoria no permitido")
    counts = {k: sum(1 for r in results if r.get("estado") == k) for k in ALLOWED}
    summary = report.get("resumen", {})
    for key, value in counts.items():
        if summary.get(key) != value:
            errors.append(f"Resumen inconsistente para {key}")
    if sum(counts.values()) != 26:
        errors.append("El resumen debe totalizar 26")
    confirmed = {r["id"] for r in results if r["estado"] == "INCUMPLIMIENTO_CONFIRMADO"}
    controlled = {r["id"] for r in results if r["estado"] == "REQUIERE_PRUEBA_CONTROLADA"}
    if set(report.get("hallazgos_confirmados_ids", [])) != confirmed:
        errors.append("Lista de incumplimientos confirmados inconsistente")
    if set(report.get("pruebas_controladas_pendientes_ids", [])) != controlled:
        errors.append("Lista de pruebas controladas inconsistente")
    if report.get("correccion_autorizada") is not False:
        errors.append("Etapa 3 no puede autorizar correcciones")
    if report.get("supabase_modificado") is not False or report.get("repositorios_eva_modificados") is not False:
        errors.append("La auditoria no puede modificar Supabase ni EVA")
    if tracking.get("etapa_4_iniciada") is not False:
        errors.append("Etapa 4 debe permanecer sin iniciar")
    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        for item in problems:
            print(f"ERROR: {item}")
        raise SystemExit(1)
    print("ETAPA_3_COMPLETADA_LINEA_BASE_SEGURIDAD: validacion correcta")
