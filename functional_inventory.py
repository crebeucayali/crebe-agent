"""Inventario funcional estático de EVA.

Cataloga qué elementos deberían ejecutar una acción en los ocho repositorios.
No pulsa controles, no envía formularios, no consulta Supabase y no modifica EVA.
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from inventory import REPOS, base_url, collect

INTERACTIVE_TAGS = {"a", "button", "form", "input", "select", "textarea", "iframe", "video", "audio", "source"}


def clean_text(value):
    return re.sub(r"\s+", " ", (value or "")).strip()


def classify_href(href):
    value = (href or "").strip()
    if not value:
        return "sin_destino"
    if value.startswith("#"):
        return "ancla_interna"
    if value.startswith("mailto:"):
        return "correo"
    if value.startswith("tel:"):
        return "telefono"
    if value.startswith("javascript:"):
        return "javascript_inline"
    host = urlsplit(value).netloc
    if host and host != "crebeucayali.github.io":
        return "enlace_externo"
    return "navegacion"


class FunctionalParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []
        self.forms = []
        self._anchor = None
        self._button = None
        self._form_stack = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        line = self.getpos()[0]
        if tag not in INTERACTIVE_TAGS:
            return
        item = {
            "tag": tag,
            "line": line,
            "id": a.get("id", ""),
            "class": a.get("class", ""),
            "name": a.get("name", ""),
            "aria_label": a.get("aria-label", ""),
            "text": "",
        }
        if tag == "a":
            item.update({"kind": classify_href(a.get("href")), "target": a.get("href", "")})
            self._anchor = item
        elif tag == "button":
            item.update({"kind": "boton", "type": a.get("type", "submit"), "onclick": a.get("onclick", "")})
            self._button = item
        elif tag == "form":
            item.update({"kind": "formulario", "method": a.get("method", "get").lower(), "target": a.get("action", "")})
            self.forms.append(item)
            self._form_stack.append(item)
        elif tag in {"input", "select", "textarea"}:
            item.update({"kind": "control_formulario", "type": a.get("type", tag), "required": "required" in a})
            if self._form_stack:
                item["form_line"] = self._form_stack[-1]["line"]
        else:
            src = a.get("src", "")
            item.update({"kind": "recurso_embebido", "target": src, "type": a.get("type", "")})
        self.elements.append(item)

    def handle_endtag(self, tag):
        if tag == "a":
            self._anchor = None
        elif tag == "button":
            self._button = None
        elif tag == "form" and self._form_stack:
            self._form_stack.pop()

    def handle_data(self, data):
        text = clean_text(data)
        if not text:
            return
        if self._anchor is not None:
            self._anchor["text"] = clean_text(self._anchor["text"] + " " + text)
        if self._button is not None:
            self._button["text"] = clean_text(self._button["text"] + " " + text)


def js_evidence(content):
    patterns = {
        "event_listener": r"addEventListener\s*\(",
        "fetch": r"\bfetch\s*\(",
        "supabase": r"\bsupabase\b|\.from\s*\(",
        "web_share": r"navigator\.share\s*\(",
        "window_open": r"window\.open\s*\(",
        "location_change": r"(?:window\.)?location(?:\.href)?\s*=",
        "local_storage": r"\blocalStorage\b",
        "session_storage": r"\bsessionStorage\b",
    }
    evidence = []
    for kind, pattern in patterns.items():
        for idx, line in enumerate(content.splitlines(), 1):
            if re.search(pattern, line, re.I):
                evidence.append({"kind": kind, "line": idx})
    return evidence


def expected_behavior(element, page_url):
    kind = element.get("kind")
    target = element.get("target", "")
    if kind in {"navegacion", "ancla_interna", "enlace_externo", "correo", "telefono"}:
        return {"action": "activar_enlace", "expected": "abrir_destino", "resolved_target": urljoin(page_url, target)}
    if kind == "formulario":
        return {"action": "enviar_formulario", "expected": "procesar_envio_segun_action_method", "resolved_target": urljoin(page_url, target) if target else page_url}
    if kind == "boton":
        return {"action": "activar_boton", "expected": "ejecutar_comportamiento_asociado", "resolved_target": None}
    if kind == "recurso_embebido":
        return {"action": "cargar_recurso", "expected": "recurso_disponible", "resolved_target": urljoin(page_url, target) if target else None}
    if kind == "control_formulario":
        return {"action": "interactuar_control", "expected": "aceptar_o_seleccionar_valor", "resolved_target": None}
    return {"action": "revisar", "expected": "comportamiento_por_definir", "resolved_target": None}


def build(snapshot, output):
    output.mkdir(parents=True, exist_ok=True)
    pages = []
    javascript = []
    totals = Counter()
    repos_seen = set()

    for source in snapshot.get("sources", []):
        repo = source["repo"]
        repos_seen.add(repo)
        path = source["path"]
        content = source["content"]
        if path.endswith(".js"):
            evidence = js_evidence(content)
            if evidence:
                javascript.append({"repo": repo, "path": path, "sha": source["sha"], "evidence": evidence})
            continue
        if not path.endswith(".html"):
            continue
        parser = FunctionalParser()
        parser.feed(content)
        page_url = urljoin(base_url(repo), path)
        elements = []
        for element in parser.elements:
            enriched = dict(element)
            enriched["expected_behavior"] = expected_behavior(element, page_url)
            enriched["label"] = clean_text(element.get("text") or element.get("aria_label") or element.get("name") or element.get("id"))
            elements.append(enriched)
            totals[enriched["kind"]] += 1
        pages.append({
            "repo": repo,
            "path": path,
            "sha": source["sha"],
            "url_expected": page_url,
            "scope": "administrativo" if re.search(r"(^|/)admin", path, re.I) else "publico_o_auxiliar",
            "functional_elements": elements,
            "counts": dict(Counter(e["kind"] for e in elements)),
        })

    per_repo = {}
    for repo in REPOS:
        repo_pages = [p for p in pages if p["repo"] == repo]
        counts = Counter()
        for page in repo_pages:
            counts.update(page["counts"])
        per_repo[repo] = {"html_pages": len(repo_pages), "functional_elements": sum(counts.values()), "by_kind": dict(counts)}

    status = "completo" if not snapshot.get("failures") and repos_seen.issuperset(REPOS) else "incompleto"
    manifest = {
        "phase": 5,
        "stage": 1,
        "name": "Inventario funcional de EVA",
        "status": status,
        "mode": "read_only_static",
        "captured_at": snapshot.get("captured_at"),
        "repositories": REPOS,
        "limits": [
            "No se activan botones ni enlaces.",
            "No se envían formularios.",
            "No se ejecuta JavaScript de EVA.",
            "No se consulta ni modifica Supabase.",
            "La presencia de un elemento no demuestra que funcione.",
            "Los resultados esperados se derivan solo cuando pueden inferirse de HTML; los botones genéricos quedan para la Etapa 2.",
        ],
        "failures": snapshot.get("failures", []),
    }
    data = {"manifest": manifest, "repositories": per_repo, "pages": pages, "javascript_evidence": javascript, "totals": dict(totals)}
    (output / "functional-inventory.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rows = []
    for repo in REPOS:
        r = per_repo[repo]
        rows.append(f"| {repo} | {r['html_pages']} | {r['functional_elements']} | {r['by_kind'].get('boton', 0)} | {r['by_kind'].get('formulario', 0)} | {r['by_kind'].get('navegacion', 0) + r['by_kind'].get('enlace_externo', 0) + r['by_kind'].get('ancla_interna', 0)} | {r['by_kind'].get('recurso_embebido', 0)} |")
    report = (
        "# Fase 5, Etapa 1: inventario funcional de EVA\n\n"
        f"Estado: {status}.\n\n"
        "Objetivo: identificar qué elementos de EVA deben ejecutar una acción antes de iniciar pruebas funcionales. Esta etapa es descriptiva y de solo lectura.\n\n"
        "| Repositorio | HTML | Elementos funcionales | Botones | Formularios | Enlaces | Recursos embebidos |\n"
        "|---|---:|---:|---:|---:|---:|---:|\n" + "\n".join(rows) + "\n\n"
        "El archivo `functional-inventory.json` conserva por página la ruta, URL esperada, huella Git, tipo de elemento, línea, etiqueta disponible, destino y comportamiento esperado inferible. También registra evidencia estática de listeners, fetch, Supabase, Web Share API, cambios de ubicación y almacenamiento del navegador.\n\n"
        "Criterio de cierre: los ocho repositorios deben estar representados y no debe haber fallos de lectura. El cierre de esta etapa no certifica que las funciones trabajen correctamente; prepara la Etapa 2, donde se definirán casos de prueba y resultados esperados.\n"
    )
    (output / "Informe_fase_5_etapa_1.md").write_text(report, encoding="utf-8")
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, help="Captura producida por inventory.py --save-snapshot")
    parser.add_argument("--output", type=Path, default=Path("reports/functional-inventory"))
    args = parser.parse_args()
    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8")) if args.snapshot else collect()
    status = build(snapshot, args.output)
    print("Inventario funcional " + status + ": " + str(args.output.resolve()))
    raise SystemExit(0 if status == "completo" else 1)


if __name__ == "__main__":
    main()
