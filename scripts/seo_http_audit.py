#!/usr/bin/env python3
"""Auditoría HTTP de los sitemaps públicos EVA. Solo GET a destinos fijos."""
import json
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

HOST = "https://crebeucayali.github.io"
PATHS = [
    "/sitemap.xml", "/sitemap-v2.xml", "/sitemap-main.xml", "/robots.txt",
    "/accesos-complementarios/sitemap.xml",
    "/capacitaciones/sitemap.xml",
    "/banco-digital-accesible/sitemap.xml",
    "/materiales-educativos-accesibles/sitemap.xml",
    "/noti-inclusivos/sitemap.xml",
    "/repositorio-accesible/sitemap.xml",
    "/DUA-3.0/sitemap.xml",
]
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"

def inspect(path):
    url = HOST + path
    entry = {"url": url, "status": None, "final_url": None, "mime": None,
             "xml_root": None, "xml_entries": None, "error": None}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CREBE-Agent-Sitemap-Audit/1.0"})
        with urllib.request.urlopen(req, timeout=18) as response:
            entry["status"] = response.status
            entry["final_url"] = response.geturl()
            entry["mime"] = response.headers.get("Content-Type", "")
            payload = response.read(2_000_000)
        if path.endswith(".xml"):
            root = ET.fromstring(payload)
            entry["xml_root"] = root.tag
            if root.tag == NS+"sitemapindex":
                entry["xml_entries"] = len(root.findall(NS+"sitemap"))
            elif root.tag == NS+"urlset":
                entry["xml_entries"] = len(root.findall(NS+"url"))
            else:
                entry["error"] = "XML root is not sitemapindex or urlset"
        else:
            text = payload.decode("utf-8", errors="replace")
            entry["sitemap_declaration"] = [line for line in text.splitlines()
                                              if line.lower().startswith("sitemap:")]
    except urllib.error.HTTPError as exc:
        entry["status"] = exc.code
        entry["error"] = "HTTP error"
    except (urllib.error.URLError, TimeoutError, ET.ParseError, ValueError) as exc:
        entry["error"] = type(exc).__name__ + ": " + str(exc)[:220]
    return entry

def main():
    results = [inspect(path) for path in PATHS]
    output = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "results": results}
    target = Path("reports/seo/http-sitemaps-latest.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    for result in results:
        print(result["status"], result["url"], "root:", result["xml_root"],
              "count:", result["xml_entries"], "error:", result["error"])
    failures = [r for r in results if r["status"] != 200 or r["error"] or
                (r["url"].endswith(".xml") and r["xml_root"] not in (NS+"sitemapindex", NS+"urlset"))]
    print("FAILURES:", len(failures), "of", len(results))
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main())
