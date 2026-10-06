from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TRACKING = ROOT / "tracking" / "fase-7.json"
SCOPE = ROOT / "config" / "fase-7-security-scope.json"
DOC = ROOT / "docs" / "FASE_7_SEGURIDAD_PERMISOS.md"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate() -> list[str]:
    errors: list[str] = []
    if not TRACKING.exists() or not SCOPE.exists() or not DOC.exists():
        return ["Faltan artefactos obligatorios de Fase 7"]
    tracking = load(TRACKING)
    scope = load(SCOPE)
    if tracking.get("fase") != 7 or tracking.get("estado") != "FASE_7_PREPARADA":
        errors.append("Estado inicial de Fase 7 invalido")
    etapas = tracking.get("etapas", [])
    if len(etapas) != 8 or [e.get("numero") for e in etapas] != list(range(1, 9)):
        errors.append("La Fase 7 debe contener exactamente 8 etapas ordenadas")
    if any(e.get("estado") != "NO_INICIADA" for e in etapas):
        errors.append("Ninguna etapa debe iniciarse durante la preparacion")
    if tracking.get("etapa_1_iniciada") is not False:
        errors.append("Etapa 1 debe permanecer sin iniciar")
    if tracking.get("repositorios_eva_modificados") is not False or tracking.get("supabase_modificado") is not False:
        errors.append("La preparacion no puede modificar EVA ni Supabase")
    rules = scope.get("reglas", {})
    required_true = [
        "solo_lectura_hasta_diagnostico",
        "no_imprimir_secretos",
        "enmascarar_evidencia_sensible",
        "publicable_key_no_es_secreto_por_si_sola",
        "service_role_o_secretos_privados_son_criticos",
        "no_relajar_RLS_para_resolver_fallos",
        "no_cambiar_permisos_sin_prueba_de_regresion",
        "una_causa_un_hallazgo",
    ]
    for key in required_true:
        if rules.get(key) is not True:
            errors.append(f"Guardrail requerido ausente: {key}")
    if rules.get("correccion_automatica") is not False:
        errors.append("La correccion automatica debe permanecer deshabilitada")
    if len(scope.get("repositorios_eva", [])) != 8:
        errors.append("El alcance debe incluir exactamente 8 repositorios EVA")
    if scope.get("supabase_project_id") != "dteimbhwtzghhsijeeld":
        errors.append("Project ID de Supabase inesperado")
    deps = scope.get("dependencias_heredadas", [])
    if not any(d.get("id") == "SEC-DEPENDENCY-001" for d in deps):
        errors.append("Debe heredarse SEC-DEPENDENCY-001")
    if tracking.get("condicion_temporal", {}).get("fecha") != "2026-10-30":
        errors.append("Falta condicion temporal Data API del 2026-10-30")
    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        for item in problems:
            print(f"ERROR: {item}")
        raise SystemExit(1)
    print("FASE_7_PREPARADA: validacion correcta")
