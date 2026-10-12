#!/usr/bin/env python3
"""Verificador de solo lectura para el Mapa Web de EVA.

Compara el Mapa Web publicado con las rutas HTML reales de los repositorios EVA,
respetando una línea base aprobada, exclusiones técnicas y redirecciones de
compatibilidad. No modifica repositorios EVA ni el Mapa Web.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
DEFAULT_BASELINE = ROOT / "tracking" / "mapa-web-baseline.json"
DEFAULT_OUTPUT = ROOT / "reports" / "mapa-web-etapa-3.json"
MAP_REPO = "crebeucayali/accesos-complementarios"
MAP_PATH = "mapa-web.html"
MAP_BASE_URL = "https://crebeucayali.github.io/accesos-complementarios/"
GITHUB_API = "https://api.github.com"
RAW_GITHUB = "https://raw.githubusercontent.com"


@dataclass
class Candidate:
    repositorio: str
    ruta: str
    url: str
    tipo: str
    marca: str | None
    estado: str
    titulo: str | None
    grupo_mapa: str
    ya_en_mapa: bool
    fuente_deteccion: str
    legado_aprobado: bool
    observacion: str
    id_seccion: str | None = None
    http_status: int | None = None
    destino_compatibilidad: str | None = None


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.body_mark: str | None = None
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self.canonical_href: str | None = None
        self.meta_refresh_target: str | None = None
        self.robots: str | None = None
        self._in_title = False
        self._in_h1 = False
        self._sections: list[dict[str, Any]] = []
        self._section_stack: list[int | None] = []
        self._heading_section: int | None = None
        self._heading_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {k.lower(): (v or "") for k, v in attrs}
        tag = tag.lower()
        if tag == "body":
            mark = data.get("data-mapa-web", "").strip().lower()
            if mark in {"publicar", "no-publicar"}:
                self.body_mark = mark
        elif tag == "link" and "canonical" in data.get("rel", "").lower().split():
            href = data.get("href", "").strip()
            if href:
                self.canonical_href = href
        elif tag == "meta":
            http_equiv = data.get("http-equiv", "").strip().lower()
            name = data.get("name", "").strip().lower()
            content = data.get("content", "").strip()
            if http_equiv == "refresh" and content:
                match = re.search(r"(?:^|;)\s*url\s*=\s*['\"]?([^'\";]+)", content, re.I)
                if match:
                    self.meta_refresh_target = match.group(1).strip()
            elif name == "robots" and content:
                self.robots = content.lower()
        elif tag == "title":
            self._in_title = True
        elif tag == "h1":
            self._in_h1 = True
        elif tag == "section":
            mark = data.get("data-mapa-web", "").strip().lower()
            idx: int | None = None
            if mark in {"publicar", "no-publicar"}:
                idx = len(self._sections)
                self._sections.append({
                    "id": data.get("id", "").strip() or None,
                    "marca": mark,
                    "titulo": None,
                })
            self._section_stack.append(idx)
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and self._section_stack:
            idx = next((x for x in reversed(self._section_stack) if x is not None), None)
            if idx is not None and not self._sections[idx]["titulo"]:
                self._heading_section = idx
                self._heading_parts = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        elif tag == "h1":
            self._in_h1 = False
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and self._heading_section is not None:
            text = clean_text("".join(self._heading_parts))
            if text:
                self._sections[self._heading_section]["titulo"] = text
            self._heading_section = None
            self._heading_parts = []
        elif tag == "section" and self._section_stack:
            self._section_stack.pop()

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_h1:
            self.h1_parts.append(data)
        if self._heading_section is not None:
            self._heading_parts.append(data)

    @property
    def title(self) -> str | None:
        h1 = clean_text("".join(self.h1_parts))
        title = clean_text("".join(self.title_parts))
        return h1 or title or None

    @property
    def sections(self) -> list[dict[str, Any]]:
        return self._sections


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        data = dict(attrs)
        href = (data.get("href") or "").strip()
        if href:
            self.hrefs.append(href)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def request_bytes(url: str, token: str | None = None, timeout: int = 25) -> bytes:
    headers = {
        "User-Agent": "crebe-agent-mapa-web/1.0",
        "Accept": "application/vnd.github+json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["X-GitHub-Api-Version"] = "2022-11-28"
    req = Request(url, headers=headers)
    with urlopen(req, timeout=timeout) as response:
        return response.read()


def request_json(url: str, token: str | None = None) -> Any:
    return json.loads(request_bytes(url, token).decode("utf-8"))


def branch_sha(repo: str, token: str | None) -> str:
    data = request_json(f"{GITHUB_API}/repos/{repo}/branches/main", token)
    return data["commit"]["sha"]


def tree_paths(repo: str, commit_sha: str, token: str | None) -> set[str]:
    commit = request_json(f"{GITHUB_API}/repos/{repo}/git/commits/{commit_sha}", token)
    tree_sha = commit["tree"]["sha"]
    tree = request_json(f"{GITHUB_API}/repos/{repo}/git/trees/{tree_sha}?recursive=1", token)
    if tree.get("truncated"):
        raise RuntimeError(f"Árbol truncado para {repo}; no se clasifica de forma incompleta.")
    return {
        item["path"]
        for item in tree.get("tree", [])
        if item.get("type") == "blob" and str(item.get("path", "")).lower().endswith(".html")
    }


def raw_text(repo: str, ref: str, path: str) -> str:
    owner, name = repo.split("/", 1)
    url = f"{RAW_GITHUB}/{owner}/{name}/{ref}/{quote(path)}"
    return request_bytes(url, None).decode("utf-8", errors="replace")


def normalize_page_path(path: str) -> str:
    path = "/" + path.lstrip("/")
    if path == "/index.html":
        return "/"
    if path.endswith("/index.html"):
        return path[: -len("index.html")]
    return path


def public_url(base_url: str, path: str) -> str:
    return urljoin(base_url, normalize_page_path(path).lstrip("/"))


def canonical_url(url: str, keep_fragment: bool = True) -> str:
    parsed = urlparse(url)
    path = parsed.path or "/"
    if path.endswith("/index.html"):
        path = path[: -len("index.html")]
    if not path:
        path = "/"
    fragment = parsed.fragment if keep_fragment else ""
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, "", "", fragment))


def is_excluded(path: str, cfg: dict[str, Any], repo_cfg: dict[str, Any]) -> tuple[bool, str | None]:
    normalized = path.replace("\\", "/").strip("/")
    lower = normalized.lower()
    parts = [p for p in lower.split("/") if p]
    excluded_segments = {x.lower() for x in cfg["global_excluded_path_segments"]}
    for part in parts[:-1]:
        if part in excluded_segments:
            return True, f"segmento técnico excluido: {part}/"
    for prefix in repo_cfg.get("extra_excluded_prefixes", []):
        if lower.startswith(prefix.lower().lstrip("/")):
            return True, f"prefijo excluido: {prefix}"
    filename = parts[-1] if parts else ""
    stem = filename.rsplit(".", 1)[0]
    for pattern in cfg["global_excluded_name_patterns"]:
        if re.search(rf"(^|[-_.]){re.escape(pattern.lower())}($|[-_.])", stem):
            return True, f"nombre técnico excluido: {pattern}"
    return False, None


def parse_page(html: str) -> PageParser:
    parser = PageParser()
    parser.feed(html)
    return parser


def compatibility_target(page: PageParser, page_url: str) -> str | None:
    """Devuelve el destino canónico solo para redirecciones inequívocas de compatibilidad.

    Se exige que exista meta refresh y canonical, que ambos resuelvan al mismo destino y
    que ese destino sea distinto de la URL actual. Así se evitan falsos positivos por el
    uso normal de canonical en páginas sustantivas.
    """
    if not page.meta_refresh_target or not page.canonical_href:
        return None
    redirect = canonical_url(urljoin(page_url, page.meta_refresh_target), keep_fragment=False)
    canonical = canonical_url(urljoin(page_url, page.canonical_href), keep_fragment=False)
    current = canonical_url(page_url, keep_fragment=False)
    if redirect == canonical and canonical != current:
        return canonical
    return None


def map_urls(html: str) -> set[str]:
    parser = LinkParser()
    parser.feed(html)
    result: set[str] = set()
    for href in parser.hrefs:
        if href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        absolute = urljoin(MAP_BASE_URL, href)
        parsed = urlparse(absolute)
        if parsed.netloc.lower() == "crebeucayali.github.io":
            result.add(canonical_url(absolute, keep_fragment=True))
    return result


def check_http(url: str) -> int | None:
    req = Request(url, headers={"User-Agent": "crebe-agent-mapa-web/1.0"}, method="HEAD")
    try:
        with urlopen(req, timeout=12) as response:
            return int(response.status)
    except HTTPError as exc:
        return int(exc.code)
    except (URLError, TimeoutError):
        return None


def classify_page(
    repo_cfg: dict[str, Any], path: str, in_baseline: bool, page: PageParser,
    published_urls: set[str], cfg: dict[str, Any], do_http: bool,
) -> Candidate:
    repo = repo_cfg["repo"]
    url = canonical_url(public_url(repo_cfg["base_url"], path))
    excluded, reason = is_excluded(path, cfg, repo_cfg)
    compat_target = compatibility_target(page, url)
    mark = page.body_mark
    already = url in published_urls
    legacy = in_baseline and not excluded and not compat_target

    if mark == "no-publicar":
        state = "NO_PUBLICAR_EN_MAPA"
        obs = "Exclusión editorial explícita mediante data-mapa-web=\"no-publicar\"."
    elif excluded:
        state = "NO_PUBLICAR_EN_MAPA"
        obs = f"Exclusión técnica: {reason}."
    elif compat_target:
        state = "NO_PUBLICAR_EN_MAPA"
        obs = f"Ruta de compatibilidad: redirige y declara como canónica {compat_target}."
    elif already:
        state = "YA_REGISTRADO"
        obs = "La ruta ya está registrada en el Mapa Web."
    elif mark == "publicar":
        state = "PUBLICAR_EN_MAPA"
        obs = "Candidata autorizada explícitamente y no registrada todavía."
    elif legacy:
        state = "PUBLICAR_EN_MAPA"
        obs = "Ruta existente al activar el verificador: LEGADO_APROBADO; falta en el Mapa Web."
    else:
        state = "PENDIENTE_CONFIRMACION"
        obs = "Ruta creada después de la línea base y sin marca data-mapa-web."

    status = check_http(url) if do_http and state != "NO_PUBLICAR_EN_MAPA" else None
    return Candidate(
        repositorio=repo,
        ruta=normalize_page_path(path),
        url=url,
        tipo="pagina",
        marca=mark,
        estado=state,
        titulo=page.title,
        grupo_mapa=repo_cfg["group"],
        ya_en_mapa=already,
        fuente_deteccion="baseline+arbol_actual" if in_baseline else "arbol_actual",
        legado_aprobado=legacy,
        observacion=obs,
        http_status=status,
        destino_compatibilidad=compat_target,
    )


def classify_sections(
    repo_cfg: dict[str, Any], path: str, page: PageParser, published_urls: set[str],
    page_excluded: bool, page_compatibility: bool, do_http: bool,
) -> list[Candidate]:
    out: list[Candidate] = []
    page_url = canonical_url(public_url(repo_cfg["base_url"], path), keep_fragment=False)
    for section in page.sections:
        sid = section.get("id")
        mark = section.get("marca")
        title = section.get("titulo")
        url = f"{page_url}#{sid}" if sid else page_url
        already = canonical_url(url) in published_urls if sid else False
        if mark == "no-publicar" or page_excluded or page_compatibility:
            state = "NO_PUBLICAR_EN_MAPA"
            obs = "Sección excluida explícitamente o contenida en una página excluida/compatibilidad."
        elif mark == "publicar" and sid and title:
            state = "YA_REGISTRADO" if already else "PUBLICAR_EN_MAPA"
            obs = "Sección navegable con marca publicar, id estable y encabezado visible."
        else:
            state = "PENDIENTE_CONFIRMACION"
            obs = "La sección marcada no cumple id estable y encabezado visible."
        status = check_http(page_url) if do_http and state != "NO_PUBLICAR_EN_MAPA" else None
        out.append(Candidate(
            repositorio=repo_cfg["repo"],
            ruta=f"{normalize_page_path(path)}#{sid}" if sid else normalize_page_path(path),
            url=url,
            tipo="seccion",
            marca=mark,
            estado=state,
            titulo=title,
            grupo_mapa=repo_cfg["group"],
            ya_en_mapa=already,
            fuente_deteccion="data-mapa-web",
            legado_aprobado=False,
            observacion=obs,
            id_seccion=sid,
            http_status=status,
        ))
    return out


def run(baseline_path: Path, output_path: Path, do_http: bool) -> dict[str, Any]:
    cfg = json.loads(baseline_path.read_text(encoding="utf-8"))
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    map_html = raw_text(MAP_REPO, "main", MAP_PATH)
    published_urls = map_urls(map_html)

    candidates: list[Candidate] = []
    current_urls: set[str] = set()
    errors: list[dict[str, str]] = []

    for repo_cfg in cfg["repositories"]:
        repo = repo_cfg["repo"]
        try:
            current_sha = branch_sha(repo, token)
            baseline_sha = repo_cfg["baseline_sha"]
            current_paths = tree_paths(repo, current_sha, token)
            baseline_paths = tree_paths(repo, baseline_sha, token)
            for path in sorted(current_paths):
                url = canonical_url(public_url(repo_cfg["base_url"], path))
                current_urls.add(url)
                excluded, _ = is_excluded(path, cfg, repo_cfg)
                try:
                    html = raw_text(repo, current_sha, path)
                    page = parse_page(html)
                    compat = compatibility_target(page, url) is not None
                except Exception as exc:  # lectura parcial no debe provocar escrituras ni suposiciones
                    candidates.append(Candidate(
                        repositorio=repo,
                        ruta=normalize_page_path(path),
                        url=url,
                        tipo="pagina",
                        marca=None,
                        estado="PENDIENTE_CONFIRMACION",
                        titulo=None,
                        grupo_mapa=repo_cfg["group"],
                        ya_en_mapa=url in published_urls,
                        fuente_deteccion="arbol_actual",
                        legado_aprobado=path in baseline_paths and not excluded,
                        observacion=f"No fue posible leer el HTML: {exc}",
                    ))
                    continue
                candidates.append(classify_page(
                    repo_cfg, path, path in baseline_paths, page, published_urls, cfg, do_http
                ))
                candidates.extend(classify_sections(
                    repo_cfg, path, page, published_urls, excluded, compat, do_http
                ))
        except Exception as exc:
            errors.append({"repositorio": repo, "error": str(exc)})

    registered_missing = sorted(
        url for url in published_urls
        if "crebeucayali.github.io" in url and "#" not in url and url not in current_urls
    )
    for url in registered_missing:
        candidates.append(Candidate(
            repositorio="desconocido",
            ruta=urlparse(url).path,
            url=url,
            tipo="pagina",
            marca=None,
            estado="RUTA_NO_DISPONIBLE",
            titulo=None,
            grupo_mapa="POR_DETERMINAR",
            ya_en_mapa=True,
            fuente_deteccion="mapa-web.html",
            legado_aprobado=False,
            observacion="La URL figura en el Mapa Web pero no coincide con una ruta HTML actual de la línea de repositorios supervisados. Requiere revisión antes de cualquier retiro.",
            http_status=check_http(url) if do_http else None,
        ))

    counts = Counter(item.estado for item in candidates)
    report = {
        "schema_version": 2,
        "stage": 3,
        "mode": "READ_ONLY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "map_source": f"{MAP_REPO}/{MAP_PATH}",
        "baseline_source": str(baseline_path.relative_to(ROOT)),
        "policy": {
            "baseline_html_outside_exclusions": "LEGADO_APROBADO",
            "future_unmarked_html": "PENDIENTE_CONFIRMACION",
            "pruebas": "NO_PUBLICAR_EN_MAPA",
            "compatibility_redirects": "NO_PUBLICAR_EN_MAPA",
            "automatic_writes": False,
        },
        "summary": dict(sorted(counts.items())),
        "errors": errors,
        "candidates": [asdict(item) for item in sorted(candidates, key=lambda x: (x.repositorio, x.ruta, x.tipo))],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verificador de solo lectura del Mapa Web EVA")
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check-http", action="store_true", help="Añade comprobación HTTP de disponibilidad sin modificar la clasificación editorial.")
    args = parser.parse_args()
    try:
        report = run(args.baseline, args.output, args.check_http)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({
        "stage": report["stage"],
        "mode": report["mode"],
        "summary": report["summary"],
        "errors": report["errors"],
        "output": str(args.output),
    }, ensure_ascii=False, indent=2))
    return 0 if not report["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
