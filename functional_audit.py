"""Fase 5, Etapa 3: auditoría funcional inicial de EVA.

Ejecuta únicamente verificaciones de lectura seguras sobre los casos de la Etapa 2.
No pulsa controles, no envía formularios, no inicia sesión y no modifica EVA o Supabase.
"""
import argparse
import json
import socket
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

ALLOWED_STATUSES = {
    "CORRECTO",
    "FALLO_CONFIRMADO",
    "REQUIERE_VERIFICACION_MANUAL",
    "NO_APLICA",
    "BLOQUEADO_POR_DEPENDENCIA",
}
READ_POLICIES = {"AUTOMATIZABLE_LECTURA", "LECTURA_SIN_EFECTOS_EXTERNOS"}
CONTROLLED_POLICIES = {"SESION_CONTROLADA_DATOS_PRUEBA", "DATOS_PRUEBA_CONTROLADOS"}
BROWSER_POLICIES = {
    "NAVEGADOR_INSTRUMENTADO_SIN_ENVIO",
    "NAVEGADOR_INSTRUMENTADO_SIN_PERSISTENCIA",
    "MANUAL_O_INSTRUMENTADA",
}


class FragmentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = set()

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if data.get("id"):
            self.targets.add(data["id"])
        if tag == "a" and data.get("name"):
            self.targets.add(data["name"])


def request_url(url, external=False, timeout=12):
    headers = {
        "User-Agent": "CREBE-Functional-Audit/1.0 (+read-only)",
        "Accept": "text/html,application/xhtml+xml,application/json;q=0.8,*/*;q=0.5",
    }
    method = "HEAD" if external else "GET"
    req = Request(url, headers=headers, method=method)
    try:
        with urlopen(req, timeout=timeout) as response:
            body = b""
            if method == "GET":
                body = response.read(2_000_000)
            return {
                "ok": 200 <= response.status < 400,
                "status": response.status,
                "final_url": response.geturl(),
                "content_type": response.headers.get("Content-Type", ""),
                "body": body.decode("utf-8", errors="replace") if body else "",
                "error": None,
            }
    except HTTPError as exc:
        if external and exc.code in {405, 501}:
            try:
                get_headers = dict(headers)
                get_headers["Range"] = "bytes=0-1023"
                with urlopen(Request(url, headers=get_headers, method="GET"), timeout=timeout) as response:
                    response.read(1024)
                    return {
                        "ok": 200 <= response.status < 400,
                        "status": response.status,
                        "final_url": response.geturl(),
                        "content_type": response.headers.get("Content-Type", ""),
                        "body": "",
                        "error": None,
                    }
            except Exception as fallback_exc:
                return _network_error(fallback_exc)
        return {
            "ok": False,
            "status": exc.code,
            "final_url": getattr(exc, "url", url),
            "content_type": exc.headers.get("Content-Type", "") if exc.headers else "",
            "body": "",
            "error": f"HTTPError:{exc.code}",
        }
    except Exception as exc:
        return _network_error(exc)


def _network_error(exc):
    if isinstance(exc, HTTPError):
        return {"ok": False, "status": exc.code, "final_url": getattr(exc, "url", None), "content_type": "", "body": "", "error": f"HTTPError:{exc.code}"}
    if isinstance(exc, URLError):
        reason = exc.reason
        name = type(reason).__name__ if reason is not None else "URLError"
        return {"ok": False, "status": None, "final_url": None, "content_type": "", "body": "", "error": name}
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return {"ok": False, "status": None, "final_url": None, "content_type": "", "body": "", "error": "Timeout"}
    return {"ok": False, "status": None, "final_url": None, "content_type": "", "body": "", "error": type(exc).__name__}


def resolved_url(case):
    target = (case.get("target") or "").strip()
    if not target:
        return case.get("page_url")
    return urljoin(case.get("page_url") or "", target)


def url_key(case):
    url = resolved_url(case) or ""
    parsed = urlsplit(url)
    if case.get("kind") == "ancla_interna":
        return parsed._replace(fragment="").geturl()
    return url


def classify_network(case, result):
    kind = case.get("kind")
    target = resolved_url(case)
    status = result.get("status")
    if result.get("ok"):
        if kind == "ancla_interna":
            fragment = urlsplit(target or "").fragment
            if not fragment:
                return "NO_APLICA", "El enlace no contiene un fragmento que pueda verificarse."
            parser = FragmentParser()
            parser.feed(result.get("body") or "")
            if fragment in parser.targets:
                return "CORRECTO", "El documento carga y contiene el destino interno indicado por el fragmento."
            return "FALLO_CONFIRMADO", "El documento carga, pero no contiene un id o name correspondiente al fragmento."
        return "CORRECTO", "El destino respondió correctamente en una verificación de lectura sin ejecutar JavaScript."
    if status in {404, 410}:
        return "FALLO_CONFIRMADO", f"El destino respondió HTTP {status}."
    if status in {401, 403, 407, 429}:
        return "BLOQUEADO_POR_DEPENDENCIA", f"La comprobación quedó limitada por una respuesta HTTP {status} del destino."
    if status is not None and 400 <= status < 600:
        return "FALLO_CONFIRMADO", f"El destino respondió HTTP {status}."
    return "BLOQUEADO_POR_DEPENDENCIA", "No se obtuvo una respuesta concluyente por una dependencia de red o del servicio externo."


def preset_status(case):
    policy = case.get("execution_policy")
    if policy in CONTROLLED_POLICIES:
        return "BLOQUEADO_POR_DEPENDENCIA", "Requiere sesión o datos de prueba controlados; no se ejecuta contra producción en esta auditoría inicial."
    if policy in BROWSER_POLICIES:
        return "REQUIERE_VERIFICACION_MANUAL", "Requiere interacción de navegador o validación manual para observar el comportamiento sin producir efectos laterales."
    if policy not in READ_POLICIES:
        return "REQUIERE_VERIFICACION_MANUAL", "La política del caso no permite una ejecución automática segura en esta etapa."
    return None


def audit(test_cases, workers=12):
    cases = test_cases.get("test_cases", [])
    cache = {}
    tasks = {}
    for case in cases:
        if preset_status(case) is not None:
            continue
        key = url_key(case)
        if not key:
            continue
        external = case.get("execution_policy") == "LECTURA_SIN_EFECTOS_EXTERNOS"
        tasks[(key, external)] = None

    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        future_map = {executor.submit(request_url, key, external): (key, external) for key, external in tasks}
        for future in as_completed(future_map):
            key = future_map[future]
            try:
                cache[key] = future.result()
            except Exception as exc:
                cache[key] = _network_error(exc)

    results = []
    statuses = Counter()
    by_repo = defaultdict(Counter)
    for case in cases:
        fixed = preset_status(case)
        if fixed is not None:
            status, detail = fixed
            evidence = {"mode": "not_executed_by_policy"}
        else:
            key = url_key(case)
            if not key:
                status, detail = "REQUIERE_VERIFICACION_MANUAL", "El caso no tiene un destino resoluble para una verificación automática."
                evidence = {"mode": "missing_target"}
            else:
                response = cache.get((key, case.get("execution_policy") == "LECTURA_SIN_EFECTOS_EXTERNOS"), {})
                status, detail = classify_network(case, response)
                evidence = {
                    "mode": "read_only_http",
                    "requested_url": key,
                    "http_status": response.get("status"),
                    "final_url": response.get("final_url"),
                    "content_type": response.get("content_type"),
                    "network_error": response.get("error"),
                }
        if status not in ALLOWED_STATUSES:
            raise RuntimeError("Estado funcional no permitido: " + str(status))
        result = dict(case)
        result.update({
            "stage_3_status": status,
            "stage_3_detail": detail,
            "stage_3_evidence": evidence,
        })
        results.append(result)
        statuses[status] += 1
        by_repo[case.get("repo")][status] += 1

    return {
        "results": results,
        "summary": {
            "total": len(results),
            "by_status": dict(statuses),
            "by_repo": {repo: dict(counter) for repo, counter in by_repo.items()},
            "unique_network_requests": len(cache),
        },
    }


def build(test_cases, output, workers=12):
    output.mkdir(parents=True, exist_ok=True)
    audited = audit(test_cases, workers=workers)
    source_total = len(test_cases.get("test_cases", []))
    complete = len(audited["results"]) == source_total and source_total > 0
    manifest = {
        "phase": 5,
        "stage": 3,
        "name": "Auditoría funcional inicial",
        "status": "completo" if complete else "incompleto",
        "mode": "controlled_read_only",
        "source_stage": 2,
        "source_cases": source_total,
        "audited_cases": len(audited["results"]),
        "allowed_statuses": sorted(ALLOWED_STATUSES),
        "limits": [
            "Solo se ejecutan automáticamente casos cuya política permite lectura segura.",
            "No se ejecuta JavaScript de EVA.",
            "No se pulsan botones ni enlaces mediante navegador.",
            "No se envían formularios.",
            "No se inicia sesión ni se usan credenciales administrativas.",
            "No se consulta ni modifica Supabase directamente.",
            "Los casos que requieren sesión, persistencia o interacción quedan bloqueados o pendientes de verificación manual.",
            "Un resultado CORRECTO valida disponibilidad y destino en modo lectura, no toda la interacción visual o JavaScript asociada.",
        ],
    }
    result = {"manifest": manifest, "summary": audited["summary"], "results": audited["results"]}
    (output / "functional-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    counts = Counter(audited["summary"]["by_status"])
    report = [
        "# Fase 5, Etapa 3: auditoría funcional inicial",
        "",
        f"Estado: {manifest['status']}.",
        "",
        f"Casos procesados: {len(audited['results'])} de {source_total}.",
        "",
        "| Estado | Casos |",
        "|---|---:|",
    ]
    for status in ["CORRECTO", "FALLO_CONFIRMADO", "REQUIERE_VERIFICACION_MANUAL", "NO_APLICA", "BLOQUEADO_POR_DEPENDENCIA"]:
        report.append(f"| {status} | {counts.get(status, 0)} |")
    report += [
        "",
        f"Solicitudes de red únicas realizadas: {audited['summary']['unique_network_requests']}.",
        "",
        "La auditoría automática se limita a lectura segura. Los casos de navegación y recursos se comprueban sin ejecutar JavaScript; los destinos externos se verifican mediante HEAD o una lectura mínima cuando HEAD no está disponible. Los casos administrativos, formularios, controles y botones que puedan requerir interacción o persistencia no se fuerzan contra producción.",
        "",
        "Los resultados de esta etapa constituyen la línea base funcional. FALLO_CONFIRMADO debe pasar a priorización y diagnóstico antes de cualquier corrección. REQUIERE_VERIFICACION_MANUAL y BLOQUEADO_POR_DEPENDENCIA no deben reinterpretarse como fallos.",
    ]
    (output / "Informe_fase_5_etapa_3.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return manifest["status"], result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True, help="functional-test-cases.json producido por la Etapa 2")
    parser.add_argument("--output", type=Path, default=Path("reports/functional-audit"))
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    test_cases = json.loads(args.cases.read_text(encoding="utf-8"))
    status, result = build(test_cases, args.output, workers=args.workers)
    print("Auditoría funcional " + status + ": " + str(result["summary"]["total"]))
    raise SystemExit(0 if status == "completo" else 1)


if __name__ == "__main__":
    main()
