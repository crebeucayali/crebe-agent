#!/usr/bin/env python3
import json
import sys
from pathlib import Path

CONTRACTS = Path("contracts/fase-6-etapa-2-integridad.json")
EXPECTED_MODULES = [
    "calendario",
    "capacitaciones",
    "noticias",
    "galeria",
    "repositorio_accesible",
    "storage_eva_publico",
    "visitas",
    "compartidos",
]
ALLOWED_VERIFICATION = {
    "STATIC_CONTRACT",
    "SCHEMA_METADATA",
    "READ_ONLY_SQL",
    "SCHEMA_AND_DATA",
    "READ_ONLY_SQL_AND_REFERENCE",
    "GRANTS_AND_RLS",
    "STORAGE_METADATA",
    "SCHEMA_AND_READ_ONLY_OBSERVATION",
    "SCHEMA_AND_GRANTS",
}


def load_contracts(path=CONTRACTS):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_contracts(data):
    errors = []
    if data.get("fase") != 6 or data.get("etapa") != 2:
        errors.append("fase/etapa incorrectas")
    if data.get("modo") != "READ_ONLY_DEFINITION":
        errors.append("modo debe ser READ_ONLY_DEFINITION")
    if data.get("escritura_habilitada") is not False:
        errors.append("escritura_habilitada debe ser false")
    if data.get("correccion_automatica") is not False:
        errors.append("correccion_automatica debe ser false")

    modules = data.get("modulos", [])
    module_ids = [m.get("id") for m in modules]
    if module_ids != EXPECTED_MODULES:
        errors.append(f"modulos inesperados: {module_ids}")

    all_ids = set()
    for rule in data.get("reglas_globales", []):
        cid = rule.get("id")
        if not cid or cid in all_ids:
            errors.append(f"id global duplicado/invalido: {cid}")
        all_ids.add(cid)
        if rule.get("verificacion") not in ALLOWED_VERIFICATION:
            errors.append(f"verificacion no permitida en {cid}")

    for expected_priority, module in enumerate(modules, start=1):
        mid = module.get("id")
        if module.get("prioridad") != expected_priority:
            errors.append(f"prioridad incorrecta en {mid}")
        contracts = module.get("contratos", [])
        if len(contracts) < 4:
            errors.append(f"{mid} tiene menos de 4 contratos")
        if not module.get("objetos"):
            errors.append(f"{mid} no declara objetos")
        for contract in contracts:
            cid = contract.get("id")
            if not cid or cid in all_ids:
                errors.append(f"id duplicado/invalido: {cid}")
            all_ids.add(cid)
            if not contract.get("descripcion"):
                errors.append(f"descripcion vacia en {cid}")
            if contract.get("verificacion") not in ALLOWED_VERIFICATION:
                errors.append(f"verificacion no permitida en {cid}")

    required = {
        "CAL-002", "CAP-002", "NOT-001", "GAL-001", "GAL-002",
        "REP-001", "STO-003", "VIS-001", "COM-001"
    }
    missing = sorted(required - all_ids)
    if missing:
        errors.append(f"faltan contratos criticos: {missing}")

    return errors


def summary(data):
    module_contracts = sum(len(m.get("contratos", [])) for m in data.get("modulos", []))
    return {
        "modules": len(data.get("modulos", [])),
        "global_rules": len(data.get("reglas_globales", [])),
        "module_contracts": module_contracts,
        "total_rules": module_contracts + len(data.get("reglas_globales", [])),
    }


def main():
    data = load_contracts()
    errors = validate_contracts(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(json.dumps(summary(data), ensure_ascii=False, indent=2))
    print("OK: contratos de integridad de Fase 6 Etapa 2 coherentes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
