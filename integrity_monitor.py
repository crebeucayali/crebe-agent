from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

CONFIG_URL = "https://crebeucayali.github.io/capacitaciones/supabase-publico.js"
EXPECTED_PROJECT = "dteimbhwtzghhsijeeld"
OUTPUT = Path("reports/runtime/fase-6-integrity-monitor.json")
UA = "crebe-agent-integrity-monitor/1.0"


def fetch_text(url: str, headers: dict[str, str] | None = None) -> str:
    req = Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urlopen(req, timeout=25) as response:
        return response.read().decode("utf-8")


def discover_public_config() -> tuple[str, str]:
    text = fetch_text(CONFIG_URL)
    url_match = re.search(r'SUPABASE_URL\s*=\s*["\'](https://[^"\']+)["\']', text)
    key_match = re.search(r'SUPABASE_PUBLISHABLE_KEY\s*=\s*["\'](sb_publishable_[^"\']+)["\']', text)
    if not url_match or not key_match:
        raise RuntimeError("No se pudo descubrir la configuracion publica desplegada de Supabase")
    base_url, key = url_match.group(1), key_match.group(1)
    if EXPECTED_PROJECT not in base_url:
        raise RuntimeError("El frontend publico apunta a un proyecto Supabase inesperado")
    return base_url.rstrip("/"), key


def rest_rows(base_url: str, key: str, table: str, params: list[tuple[str, str]]) -> list[dict]:
    url = f"{base_url}/rest/v1/{table}?{urlencode(params)}"
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Accept": "application/json"}
    data = json.loads(fetch_text(url, headers))
    if not isinstance(data, list):
        raise RuntimeError(f"Respuesta inesperada de {table}")
    return data


def storage_ok(url: str) -> bool:
    req = Request(url, headers={"User-Agent": UA}, method="HEAD")
    try:
        with urlopen(req, timeout=20) as response:
            return 200 <= response.status < 400
    except Exception:
        try:
            req = Request(url, headers={"User-Agent": UA, "Range": "bytes=0-0"})
            with urlopen(req, timeout=20) as response:
                return 200 <= response.status < 400
        except Exception:
            return False


def run_monitor() -> dict:
    base_url, key = discover_public_config()
    alerts: list[dict] = []

    actividades = rest_rows(base_url, key, "calendario_actividades", [("select", "id"), ("visible", "eq.true")])
    capacitaciones = rest_rows(base_url, key, "capacitaciones_sesiones", [("select", "id"), ("visible", "eq.true")])
    calendario = rest_rows(base_url, key, "calendario_publico", [("select", "registro_id")])
    cap_proyectadas = [r for r in calendario if str(r.get("registro_id", "")).startswith("capacitacion-")]

    if len(calendario) != len(actividades) + len(capacitaciones):
        alerts.append({"id": "MON-CAL-001", "detalle": "La vista calendario_publico no coincide con la suma de fuentes visibles"})
    if len(cap_proyectadas) != len(capacitaciones):
        alerts.append({"id": "MON-CAP-001", "detalle": "La proyeccion de capacitaciones en calendario_publico no es uno-a-uno"})

    noticias = rest_rows(base_url, key, "noticias_destacadas", [("select", "id,imagen_url"), ("visible", "eq.true"), ("estado_publicacion", "eq.publicado")])
    galeria = rest_rows(base_url, key, "galeria_items", [("select", "id,imagen_url"), ("visible", "eq.true"), ("publicacion_autorizada", "eq.true"), ("estado_publicacion", "eq.publicado")])
    galeria_imgs = rest_rows(base_url, key, "galeria_item_imagenes", [("select", "galeria_item_id,imagen_url")])
    repositorio = rest_rows(base_url, key, "repositorio_recursos", [("select", "id,imagen_url"), ("visible", "eq.true"), ("estado_publicacion", "eq.publicado")])

    public_gallery_ids = {r["id"] for r in galeria if "id" in r}
    orphan_visible_children = [r for r in galeria_imgs if r.get("galeria_item_id") not in public_gallery_ids]
    if orphan_visible_children:
        alerts.append({"id": "MON-GAL-001", "detalle": "Hay imagenes de galeria visibles sin padre publico correspondiente", "cantidad": len(orphan_visible_children)})

    referenced_urls: set[str] = set()
    for rows in (noticias, galeria, galeria_imgs, repositorio):
        for row in rows:
            value = row.get("imagen_url")
            if isinstance(value, str) and "/storage/v1/object/public/eva-publico/" in value:
                referenced_urls.add(value)

    missing_urls = sorted(url for url in referenced_urls if not storage_ok(url))
    if missing_urls:
        alerts.append({"id": "MON-STO-001", "detalle": "Existen referencias publicas a objetos Storage no accesibles", "cantidad": len(missing_urls), "urls": missing_urls})

    return {
        "schema_version": 1,
        "fase": 6,
        "etapa": 8,
        "estado": "OK" if not alerts else "ALERTA",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "modo": "PUBLIC_READ_ONLY",
        "project_id": EXPECTED_PROJECT,
        "observado": {
            "actividades_visibles": len(actividades),
            "capacitaciones_visibles": len(capacitaciones),
            "calendario_publico": len(calendario),
            "capacitaciones_proyectadas": len(cap_proyectadas),
            "noticias_publicas": len(noticias),
            "galeria_publica": len(galeria),
            "galeria_imagenes_visibles": len(galeria_imgs),
            "repositorio_publico": len(repositorio),
            "storage_referencias_publicas_unicas": len(referenced_urls),
            "storage_referencias_faltantes": len(missing_urls),
        },
        "alertas": alerts,
        "notas": [
            "No ejecuta INSERT, UPDATE, DELETE ni RPC de escritura.",
            "Visitas/Compartidos, RLS/GRANT y candidatos Storage requieren auditoria profunda separada para evitar contaminar produccion.",
            "La clave publicable se descubre desde el frontend publico desplegado y no se guarda en el reporte.",
        ],
    }


def main() -> int:
    try:
        report = run_monitor()
    except Exception as exc:
        report = {"schema_version": 1, "fase": 6, "etapa": 8, "estado": "BLOQUEADO", "error": str(exc)}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("estado") == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
