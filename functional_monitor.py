"""Fase 5, Etapa 8: monitoreo funcional recurrente de EVA.

Comprueba un conjunto pequeño de URLs centinela mediante lectura HTTP segura.
No ejecuta JavaScript, no envía formularios, no inicia sesión y no modifica EVA.
"""
import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def request_url(url, timeout=15):
    req = Request(
        url,
        headers={
            "User-Agent": "CREBE-Functional-Monitor/1.0 (+read-only)",
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.5",
            "Cache-Control": "no-cache",
        },
        method="GET",
    )
    try:
        with urlopen(req, timeout=timeout) as response:
            body = response.read(1_000_000).decode("utf-8", errors="replace")
            return {
                "status": response.status,
                "final_url": response.geturl(),
                "body": body,
                "error": None,
            }
    except HTTPError as exc:
        return {
            "status": exc.code,
            "final_url": getattr(exc, "url", url),
            "body": "",
            "error": f"HTTPError:{exc.code}",
        }
    except URLError as exc:
        return {
            "status": None,
            "final_url": None,
            "body": "",
            "error": type(exc.reason).__name__,
        }
    except Exception as exc:
        return {
            "status": None,
            "final_url": None,
            "body": "",
            "error": type(exc).__name__,
        }


def evaluate(target, response):
    status = response.get("status")
    if status is None:
        return "ALERTA", "No se obtuvo respuesta concluyente del destino."
    allowed = target.get("allowed_statuses", list(range(200, 400)))
    if status not in allowed:
        return "ALERTA", f"Respuesta HTTP inesperada: {status}."
    body = response.get("body") or ""
    for text in target.get("must_contain", []):
        if text not in body:
            return "ALERTA", f"No se encontró el marcador esperado: {text}"
    for text in target.get("must_not_contain", []):
        if text in body:
            return "ALERTA", f"Se encontró un marcador que debía permanecer ausente: {text}"
    return "CORRECTO", "El centinela respondió según lo esperado."


def run(config):
    results = []
    counts = Counter()
    for target in config.get("targets", []):
        response = request_url(target["url"])
        status, detail = evaluate(target, response)
        counts[status] += 1
        results.append({
            "id": target["id"],
            "name": target["name"],
            "repo": target.get("repo"),
            "url": target["url"],
            "criticality": target.get("criticality", "NORMAL"),
            "status": status,
            "detail": detail,
            "http_status": response.get("status"),
            "final_url": response.get("final_url"),
            "network_error": response.get("error"),
        })
    return {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": len(results),
            "correct": counts.get("CORRECTO", 0),
            "alerts": counts.get("ALERTA", 0),
            "known_exceptions": len(config.get("known_exceptions", [])),
        },
        "known_exceptions": config.get("known_exceptions", []),
        "results": results,
    }


def build(config, output):
    output.mkdir(parents=True, exist_ok=True)
    result = run(config)
    (output / "functional-monitor.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Monitoreo funcional recurrente de EVA",
        "",
        f"Centinelas comprobados: {result['summary']['total']}.",
        f"Correctos: {result['summary']['correct']}.",
        f"Alertas: {result['summary']['alerts']}.",
        f"Excepciones conocidas: {result['summary']['known_exceptions']}.",
        "",
        "| Centinela | Estado | HTTP |",
        "|---|---|---:|",
    ]
    for item in result["results"]:
        lines.append(f"| {item['name']} | {item['status']} | {item['http_status'] or '-'} |")
    if result["known_exceptions"]:
        lines += ["", "## Excepciones conocidas"]
        for item in result["known_exceptions"]:
            lines.append(f"- `{item['id']}`: {item['reason']}")
    (output / "Informe_monitoreo_funcional.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/functional-monitor-targets.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/functional-monitor"),
    )
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    result = build(config, args.output)
    print(json.dumps(result["summary"], ensure_ascii=False))
    raise SystemExit(2 if result["summary"]["alerts"] else 0)


if __name__ == "__main__":
    main()
