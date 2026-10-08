#!/usr/bin/env python3
"""Valida el cierre formal de la Fase 8 Etapa 7 contra evidencia generada en solo lectura."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "reports" / "fase-8-etapa-7-correccion-accesibilidad.json"
TRACKING = ROOT / "tracking" / "fase-8-etapa-7.json"
PHASE = ROOT / "tracking" / "fase-8.json"
EXPECTED_STATE = "ETAPA_7_COMPLETADA_CORRECCION_CONTROLADA_ACCESIBILIDAD"


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    generated_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "reports" / "fase-8-etapa-7-verificacion.generated.json"
    generated = load(generated_path)
    report = load(REPORT)
    tracking = load(TRACKING)
    phase = load(PHASE)

    require(generated.get("fase") == 8 and generated.get("etapa") == 7, "La evidencia generada no corresponde a Fase 8 Etapa 7")
    require(generated.get("modo") == "READ_ONLY_POST_CORRECTION_VERIFICATION", "Modo de verificacion inesperado")
    require(generated.get("paginas_funcionales_observadas") == 63, "El universo funcional verificado debe ser 63 paginas")
    require(generated.get("paginas_no_cargadas") == 0, "Existen paginas funcionales no cargadas")
    require(generated.get("contraste", {}).get("nodos_restantes") == 0, "Persisten nodos de contraste")
    require(generated.get("reflujo", {}).get("targets_verificados") == 4, "Deben verificarse las 4 URLs objetivo de reflujo")
    require(generated.get("reflujo", {}).get("targets_con_overflow") == 0, "Persisten desbordamientos a 320 px")
    require(generated.get("guardrails", {}).get("repositorios_eva_modificados_por_verificador") is False, "El verificador no debe modificar EVA")
    require(generated.get("guardrails", {}).get("supabase_modificado") is False, "El verificador no debe modificar Supabase")
    require(generated.get("guardrails", {}).get("etapa_8_iniciada") is False, "El verificador no debe iniciar Etapa 8")

    require(report.get("estado") == EXPECTED_STATE, "Estado de reporte de Etapa 7 inesperado")
    final = report.get("verificacion_final", {})
    require(final.get("estado") == "APROBADA_POST_CORRECCION_ETAPA_7", "La verificacion final no esta aprobada")
    require(final.get("paginas_verificadas") == generated.get("paginas_funcionales_observadas"), "No coincide el numero de paginas verificadas")
    require(final.get("fallos_carga") == generated.get("paginas_no_cargadas"), "No coincide el numero de fallos de carga")
    require(final.get("nodos_contraste") == generated.get("contraste", {}).get("nodos_restantes"), "No coincide el residuo de contraste")
    require(final.get("urls_objetivo_reflujo") == generated.get("reflujo", {}).get("targets_verificados"), "No coincide el numero de URLs de reflujo")
    require(final.get("fallos_overflow_320") == generated.get("reflujo", {}).get("targets_con_overflow"), "No coincide el residuo de overflow")
    require(len(report.get("intervenciones", [])) == 9, "El cierre debe registrar 9 PRs/intervenciones EVA")
    require(report.get("guardrails", {}).get("etapa_8_iniciada") is False, "El reporte no debe iniciar Etapa 8")

    require(tracking.get("estado") == EXPECTED_STATE, "Tracking de Etapa 7 inesperado")
    require(tracking.get("pull_requests_eva") == 9, "Tracking debe registrar 9 PRs EVA")
    tfinal = tracking.get("verificacion_final", {})
    require(tfinal.get("estado") == "APROBADA_POST_CORRECCION_ETAPA_7", "Tracking no registra aprobacion post-correccion")
    require(tfinal.get("nodos_contraste") == 0 and tfinal.get("fallos_overflow_320") == 0, "Tracking conserva residuos de accesibilidad")
    require(tracking.get("etapa_8_iniciada") is False, "Tracking de Etapa 7 no debe iniciar Etapa 8")

    require(phase.get("etapa_7", {}).get("estado") == EXPECTED_STATE, "Fase 8 no registra Etapa 7 completada")
    require(phase.get("etapa_7", {}).get("resultado", {}).get("pull_requests_eva") == 9, "Fase 8 debe registrar 9 PRs EVA")
    require(phase.get("etapa_7", {}).get("verificacion_post_correccion", {}).get("nodos_contraste") == 0, "Fase 8 conserva contraste residual")
    require(phase.get("etapa_7", {}).get("verificacion_post_correccion", {}).get("fallos_overflow_320") == 0, "Fase 8 conserva overflow residual")
    require(phase.get("etapa_7", {}).get("etapa_8_iniciada") is False, "Etapa 8 no debe estar iniciada")
    require(phase.get("etapas", [])[7].get("estado") == "NO_INICIADA", "Etapa 8 debe permanecer NO_INICIADA")

    print("Fase 8 Etapa 7: cierre formal y evidencia post-correccion coherentes (contraste=0, overflow=0).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
