#!/usr/bin/env python3
"""Audita el favicon institucional en las URLs de los sitemaps oficiales EVA.

Uso: python3 scripts/verify_eva_favicon.py
Solo lectura: no altera paginas ni repositorios.
"""
from __future__ import annotations
import json
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

BASE = "https://crebeucayali.github.io/"
EXPECTED = BASE + "materiales-educativos-accesibles/logo-crebe.webp"
SITEMAP = BASE + "sitemap-v2.xml"
UA = "CREBE-EVA-Favicon-Audit/1.0"
ICON = re.compile(r'<link\b[^>]*\brel\s*=\s*["\'][^"\']*(?:shortcut\s+)?icon[^"\']*["\'][^>]*>', re.I)
HREF = re.compile(r'\bhref\s*=\s*["\']([^"\']+)["\']', re.I)

def request(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()

def sitemap_urls(url: str) -> list[str]:
    root = ET.fromstring(request(url))
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    children = [n.text.strip() for n in root.findall("./s:sitemap/s:loc", ns) if n.text]
    if children:
        out = []
        for child in children:
            out.extend(sitemap_urls(child))
        return out
    return [n.text.strip() for n in root.findall("./s:url/s:loc", ns) if n.text]

def verify() -> int:
    urls = list(dict.fromkeys(sitemap_urls(SITEMAP)))
    rows = []
    for url in urls:
        try:
            page = request(url).decode("utf-8", "replace")
            icons = ICON.findall(page)
            hrefs = [m.group(1) for icon in icons if (m := HREF.search(icon))]
            status = "ok" if EXPECTED in hrefs else "missing_or_different"
            rows.append({"url": url, "status": status, "icons": hrefs})
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            rows.append({"url": url, "status": "request_error", "error": str(exc)})
    summary = {"checked": len(rows), "ok": sum(r["status"] == "ok" for r in rows),
               "missing_or_different": sum(r["status"] == "missing_or_different" for r in rows),
               "request_error": sum(r["status"] == "request_error" for r in rows),
               "expected": EXPECTED, "results": rows}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] == summary["checked"] else 1

if __name__ == "__main__":
    sys.exit(verify())
