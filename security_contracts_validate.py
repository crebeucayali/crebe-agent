from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTRACTS = ROOT / "contracts" / "fase-7-etapa-2-contratos-seguridad.json"
TRACKING = ROOT / "tracking" / "fase-7-etapa-2.json"

REQUIRED_SURFACES = {f"SEC-SURFACE-00{i}" for i in range(1, 7)}
REQUIRED_RESULTS = {
    "CUMPLE",
    "INCUMPLIMIENTO_CONFIRMADO",
    "REQUIERE_PRUEBA_CONTROLADA",
    "REQUIERE_REVISION_MANUAL",
    "NO_APLICA",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate() -> list[str]:
    errors: list[str] = []
    if not CONTRACTS.exists() or not TRACKING.exists():
        return ["Faltan artefactos obligatorios de Etapa 2"]
    data = load(CONTRACTS)
    tracking = load(TRACKING)
    if data.get("fase") != 7 or data.get("etapa") != 2:
        errors.append("Contrato fuera de Fase 7 Etapa 2")
    if data.get("modo") != "READ_ONLY_DEFINITION":
        errors.append("Etapa 2 debe ser definicion de solo lectura")
    contracts = data.get("contratos", [])
    ids = [item.get("id") for item in contracts]
    if len(contracts) != 26 or data.get("total_contratos") != 26:
        errors.append("Se esperaban 26 contratos")
    if len(ids) != len(set(ids)):
        errors.append("Hay IDs de contrato duplicados")
    if set(data.get("superficies_cubiertas", [])) != REQUIRED_SURFACES:
        errors.append("No estan cubiertas las seis superficies de Etapa 1")
    if set(data.get("resultados_auditoria", [])) != REQUIRED_RESULTS:
        errors.append("Estados de auditoria incompletos")
    text = json.dumps(data, ensure_ascii=False).lower()
    if "service_role_no_debe_aparecer_en_cliente" not in text:
        errors.append("Falta guardrail service_role")
    if data.get("correccion_autorizada") is not False:
        errors.append("Etapa 2 no puede autorizar correccion")
    if data.get("supabase_modificado") is not False or data.get("repositorios_eva_modificados") is not False:
        errors.append("Etapa 2 no puede modificar produccion")
    if tracking.get("estado") != "ETAPA_2_COMPLETADA_CONTRATOS_SEGURIDAD":
        errors.append("Tracking de Etapa 2 invalido")
    if tracking.get("etapa_3_iniciada") is not False:
        errors.append("Etapa 3 debe permanecer sin iniciar")
    return errors


if __name__ == "__main__":
    issues = validate()
    if issues:
        for item in issues:
            print(f"ERROR: {item}")
        raise SystemExit(1)
    print("ETAPA_2_COMPLETADA_CONTRATOS_SEGURIDAD: validacion correcta")
