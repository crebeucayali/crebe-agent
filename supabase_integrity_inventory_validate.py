"""Valida el inventario comprometido de la Fase 6, Etapa 1.

No conecta a Supabase y no modifica EVA. Solo comprueba coherencia interna del
artefacto de inventario previamente capturado en modo lectura.
"""
import argparse
import json
from pathlib import Path

REQUIRED_OBJECTS = {
    "public.calendario_actividades",
    "public.calendario_publico",
    "public.capacitaciones_sesiones",
    "public.noticias_destacadas",
    "public.galeria_items",
    "public.galeria_item_imagenes",
    "public.repositorio_recursos",
    "public.eva_visitas_eventos",
    "public.eva_visitas_diarias",
    "public.eva_compartidos_eventos",
    "public.eva_compartidos_diarios",
    "storage:eva-publico",
}

REQUIRED_MODULES = {
    "calendario",
    "capacitaciones",
    "noticias",
    "galeria",
    "repositorio_accesible",
    "administracion",
}


def validate(data):
    errors = []
    if data.get("phase") != 6 or data.get("stage") != 1:
        errors.append("fase/etapa incorrectas")
    if data.get("mode") != "READ_ONLY":
        errors.append("el inventario debe declarar modo READ_ONLY")
    if data.get("project", {}).get("id") != "dteimbhwtzghhsijeeld":
        errors.append("project_id inesperado")

    objects = {item.get("name"): item for item in data.get("objects", [])}
    missing = sorted(REQUIRED_OBJECTS - set(objects))
    if missing:
        errors.append("objetos faltantes: " + ", ".join(missing))

    calendar = objects.get("public.calendario_actividades", {})
    trainings = objects.get("public.capacitaciones_sesiones", {})
    public_view = objects.get("public.calendario_publico", {})
    if calendar and trainings and public_view:
        expected = calendar.get("visible_rows", 0) + trainings.get("visible_rows", 0)
        if public_view.get("rows") != expected:
            errors.append("calendario_publico no cuadra con las dos fuentes visibles")
        if public_view.get("security_invoker") is not True:
            errors.append("calendario_publico debe registrar security_invoker=true")

    gallery_images = objects.get("public.galeria_item_imagenes", {})
    fks = gallery_images.get("foreign_keys", [])
    if not any(fk.get("references") == "public.galeria_items.id" for fk in fks):
        errors.append("falta relación galeria_item_imagenes -> galeria_items")

    storage = objects.get("storage:eva-publico", {})
    if storage:
        prefix_total = sum(storage.get("prefixes", {}).values())
        if prefix_total != storage.get("objects"):
            errors.append("conteo Storage no cuadra con sus prefijos")

    consumers = {item.get("module") for item in data.get("frontend_consumers", [])}
    missing_consumers = sorted(REQUIRED_MODULES - consumers)
    if missing_consumers:
        errors.append("consumidores faltantes: " + ", ".join(missing_consumers))

    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=Path("baselines/fase-6-etapa-1-inventario.json"))
    args = parser.parse_args()
    data = json.loads(args.inventory.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit(1)
    print("Inventario Fase 6 Etapa 1 coherente:", len(data.get("objects", [])), "objetos")


if __name__ == "__main__":
    main()
