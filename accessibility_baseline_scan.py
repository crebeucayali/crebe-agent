from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

REPOS = [
    "crebeucayali.github.io",
    "accesos-complementarios",
    "capacitaciones",
    "banco-digital-accesible",
    "materiales-educativos-accesibles",
    "noti-inclusivos",
    "repositorio-accesible",
    "DUA-3.0",
]

REFERENCE_HTML_PAGES = 65
STATUS_OK = "CUMPLE"
STATUS_FAIL = "INCUMPLIMIENTO_CONFIRMADO"
STATUS_CONTROLLED = "REQUIERE_VERIFICACION_CONTROLADA"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_lang = None
        self.title_depth = 0
        self.title_parts: list[str] = []
        self.images = 0
        self.images_missing_alt = 0
        self.buttons = 0
        self.anchors = 0
        self.controls_missing_name = 0
        self.form_controls = 0
        self.form_controls_missing_label = 0
        self.labels_for: set[str] = set()
        self.pending_controls: list[dict[str, Any]] = []
        self._interactive_stack: list[dict[str, Any]] = []
        self._label_depth = 0

    @staticmethod
    def attrs_dict(attrs):
        return {str(k).lower(): ("" if v is None else str(v)) for k, v in attrs}

    @staticmethod
    def has_direct_name(attrs: dict[str, str]) -> bool:
        return any(attrs.get(k, "").strip() for k in ("aria-label", "aria-labelledby", "title"))

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        a = self.attrs_dict(attrs)
        if tag == "html":
            self.html_lang = a.get("lang", "").strip()
        elif tag == "title":
            self.title_depth += 1
        elif tag == "img":
            self.images += 1
            if "alt" not in a:
                self.images_missing_alt += 1
            if self._interactive_stack and a.get("alt", "").strip():
                self._interactive_stack[-1]["text"].append(a["alt"].strip())
        elif tag == "label":
            self._label_depth += 1
            target = a.get("for", "").strip()
            if target:
                self.labels_for.add(target)
        elif tag in ("button", "a"):
            if tag == "a" and not a.get("href", "").strip() and not a.get("role", "").strip():
                return
            if tag == "button":
                self.buttons += 1
            else:
                self.anchors += 1
            self._interactive_stack.append({"tag": tag, "attrs": a, "text": []})
        elif tag in ("input", "select", "textarea"):
            input_type = a.get("type", "text").lower() if tag == "input" else tag
            if input_type == "hidden":
                return
            self.form_controls += 1
            self.pending_controls.append({"attrs": a, "implicit_label": self._label_depth > 0})

    def handle_startendtag(self, tag: str, attrs) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() in ("button", "a", "label"):
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title" and self.title_depth:
            self.title_depth -= 1
        elif tag == "label" and self._label_depth:
            self._label_depth -= 1
        if tag in ("button", "a") and self._interactive_stack:
            item = self._interactive_stack.pop()
            if item["tag"] != tag:
                return
            a = item["attrs"]
            text = " ".join(item["text"]).strip()
            if not text and not self.has_direct_name(a):
                self.controls_missing_name += 1

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_parts.append(data)
        if self._interactive_stack and data.strip():
            self._interactive_stack[-1]["text"].append(data.strip())

    def finalize(self) -> None:
        for item in self.pending_controls:
            a = item["attrs"]
            control_id = a.get("id", "").strip()
            input_type = a.get("type", "text").lower()
            if item["implicit_label"]:
                continue
            if input_type in ("submit", "reset", "button") and a.get("value", "").strip():
                continue
            if input_type == "image" and a.get("alt", "").strip():
                continue
            if self.has_direct_name(a):
                continue
            if control_id and control_id in self.labels_for:
                continue
            self.form_controls_missing_label += 1

    @property
    def title(self) -> str:
        return " ".join(" ".join(self.title_parts).split()).strip()


def scan_page(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    p = PageParser()
    p.feed(text)
    p.finalize()
    return {
        "lang_missing": not bool(p.html_lang),
        "title_missing": not bool(p.title),
        "images": p.images,
        "images_missing_alt": p.images_missing_alt,
        "buttons": p.buttons,
        "anchors": p.anchors,
        "controls_missing_name": p.controls_missing_name,
        "form_controls": p.form_controls,
        "form_controls_missing_label": p.form_controls_missing_label,
    }


def baseline(root: Path) -> dict[str, Any]:
    totals = Counter()
    repo_results: dict[str, Any] = {}
    evidence_pages: dict[str, list[str]] = defaultdict(list)

    for repo in REPOS:
        repo_dir = root / repo
        if not repo_dir.is_dir():
            raise SystemExit(f"Repositorio ausente en lectura: {repo_dir}")
        pages = sorted(p for p in repo_dir.rglob("*.html") if ".git" not in p.parts)
        repo_counter = Counter()
        for page in pages:
            r = scan_page(page)
            repo_counter["paginas_html"] += 1
            for key, value in r.items():
                if isinstance(value, bool):
                    if value:
                        repo_counter[key] += 1
                        if len(evidence_pages[key]) < 50:
                            evidence_pages[key].append(f"{repo}/{page.relative_to(repo_dir).as_posix()}")
                else:
                    repo_counter[key] += int(value)
                    if key in {"images_missing_alt", "controls_missing_name", "form_controls_missing_label"} and value:
                        if len(evidence_pages[key]) < 50:
                            evidence_pages[key].append(f"{repo}/{page.relative_to(repo_dir).as_posix()}")
        repo_results[repo] = dict(repo_counter)
        totals.update(repo_counter)

    contracts: list[dict[str, Any]] = []
    always_controlled = {
        "A11Y-CON-002", "A11Y-CON-004", "A11Y-CON-006", "A11Y-CON-007", "A11Y-CON-008",
        "A11Y-CON-011", "A11Y-CON-012", "A11Y-CON-013", "A11Y-CON-014", "A11Y-CON-015",
        "A11Y-CON-016", "A11Y-CON-017", "A11Y-CON-018", "A11Y-CON-019", "A11Y-CON-020",
        "A11Y-CON-021", "A11Y-CON-022", "A11Y-CON-023", "A11Y-CON-024", "A11Y-CON-025",
        "A11Y-CON-026", "A11Y-CON-027", "A11Y-CON-028",
    }

    static_structural = {
        "A11Y-CON-001": ("images_missing_alt", "imagenes sin atributo alt"),
        "A11Y-CON-003": ("controls_missing_name", "botones/enlaces sin nombre accesible estatico"),
    }
    candidate_only = {
        "A11Y-CON-005": ("form_controls_missing_label", "controles de formulario candidatos sin etiqueta/nombre programatico estatico"),
        "A11Y-CON-009": ("lang_missing", "HTML observados sin idioma principal programatico; requieren confirmar pertenencia al universo funcional"),
        "A11Y-CON-010": ("title_missing", "HTML observados sin titulo no vacio; requieren confirmar pertenencia al universo funcional y utilidad del titulo"),
    }

    for n in range(1, 29):
        cid = f"A11Y-CON-{n:03d}"
        if cid in static_structural:
            metric, description = static_structural[cid]
            count = int(totals.get(metric, 0))
            contracts.append({
                "id": cid,
                "estado": STATUS_FAIL if count else STATUS_OK,
                "evidencia": {
                    "metrica": metric,
                    "descripcion": description,
                    "cantidad": count,
                    "muestra_paginas": evidence_pages.get(metric, [])[:20],
                    "nota": "El estado se limita al requisito estructural automatizable y no constituye declaracion global de conformidad WCAG.",
                },
                "alcance_evidencia": "ESTATICA_ESTRUCTURAL",
            })
        elif cid in candidate_only:
            metric, description = candidate_only[cid]
            count = int(totals.get(metric, 0))
            contracts.append({
                "id": cid,
                "estado": STATUS_CONTROLLED,
                "evidencia": {
                    "metrica": metric,
                    "descripcion": description,
                    "cantidad_candidatos": count,
                    "muestra_paginas": evidence_pages.get(metric, [])[:20],
                    "motivo": "La evidencia estatica identifica candidatos, pero no basta para confirmar incumplimiento sin validar contexto funcional, etiquetado implicito/dinamico o semantica efectiva.",
                },
                "alcance_evidencia": "CANDIDATOS_PARA_VERIFICACION_CONTROLADA",
            })
        elif cid in always_controlled:
            contracts.append({
                "id": cid,
                "estado": STATUS_CONTROLLED,
                "evidencia": {"motivo": "El contrato requiere interaccion, arbol de accesibilidad, medicion visual o juicio semantico; no se infiere cumplimiento ni fallo desde HTML estatico."},
                "alcance_evidencia": "NO_CONCLUIDO_EN_ANALISIS_ESTATICO",
            })
        else:
            raise AssertionError(cid)

    status_counts = Counter(c["estado"] for c in contracts)
    observed_pages = int(totals.get("paginas_html", 0))
    return {
        "schema_version": 2,
        "fase": 8,
        "etapa": 3,
        "nombre": "Linea base de accesibilidad",
        "modo": "READ_ONLY_BASELINE",
        "repositorios_eva_modificados": False,
        "universo": {
            "repositorios": len(REPOS),
            "paginas_html_referencia_etapa_1": REFERENCE_HTML_PAGES,
            "paginas_html_observadas_actualmente": observed_pages,
            "diferencia_desde_referencia": observed_pages - REFERENCE_HTML_PAGES,
            "tratamiento_diferencia": "REQUIERE_VERIFICACION_CONTROLADA; no se interpreta como fallo de accesibilidad ni se fuerza el conteo historico.",
        },
        "metricas_estaticas": dict(totals),
        "por_repositorio": repo_results,
        "contratos": contracts,
        "resumen_contratos": {
            STATUS_OK: int(status_counts.get(STATUS_OK, 0)),
            STATUS_FAIL: int(status_counts.get(STATUS_FAIL, 0)),
            STATUS_CONTROLLED: int(status_counts.get(STATUS_CONTROLLED, 0)),
            "total": len(contracts),
        },
        "guardrails": {
            "sin_correcciones": True,
            "sin_severidades": True,
            "sin_priorizacion": True,
            "sin_forzar_universo_historico": True,
            "etapa_4_no_iniciada": True,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    data = baseline(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data["resumen_contratos"], ensure_ascii=False))


if __name__ == "__main__":
    main()
