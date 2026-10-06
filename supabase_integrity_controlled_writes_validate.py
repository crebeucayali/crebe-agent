from __future__ import annotations

import json
from pathlib import Path

REPORT = Path("reports/fase-6-etapa-5-pruebas-controladas.json")

REQUIRED_TRUE = {
    "calendario_insert_update_ok",
    "capacitacion_insert_update_ok",
    "noticia_insert_update_ok",
    "galeria_padre_ok",
    "galeria_hija_ok",
    "galeria_on_delete_cascade_ok",
    "repositorio_insert_update_ok",
    "visitas_global_trigger_ok",
    "visitas_modulo_trigger_ok",
    "compartidos_trigger_ok",
    "visitas_eventos_efimeros_ok",
    "compartidos_eventos_efimeros_ok",
}


def validate_report(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("estado") != "ETAPA_5_COMPLETADA_PRUEBAS_CONTROLADAS":
        errors.append("estado inesperado")
    if data.get("modo") != "CONTROLLED_TRANSACTION_ROLLBACK":
        errors.append("modo inseguro")
    result = data.get("resultado_final", {})
    missing = REQUIRED_TRUE - set(result)
    if missing:
        errors.append(f"checks faltantes: {sorted(missing)}")
    for key in REQUIRED_TRUE:
        if result.get(key) is not True:
            errors.append(f"check no exitoso: {key}")
    rollback = data.get("rollback", {})
    if rollback.get("ejecutado") is not True:
        errors.append("rollback no confirmado")
    for key, value in rollback.items():
        if key != "ejecutado" and value != 0:
            errors.append(f"residuo detectado: {key}={value}")
    if data.get("supabase_modificado_durablemente") is not False:
        errors.append("se declara modificacion durable de Supabase")
    if data.get("repositorios_eva_modificados") is not False:
        errors.append("se declara modificacion de EVA")
    if data.get("hallazgos_confirmados") != 0:
        errors.append("la etapa no deberia cerrar con hallazgos confirmados")
    return errors


def main() -> int:
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    errors = validate_report(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Etapa 5 valida: pruebas controladas reversibles sin residuos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
