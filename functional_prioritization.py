"""Fase 5, Etapa 4: clasificacion y priorizacion de hallazgos funcionales.

Consume la auditoria funcional de la Etapa 3. Agrupa los casos FALLO_CONFIRMADO
por causa/destino, calcula impacto y prioridad, y no modifica EVA.
"""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def finding_id(target):
    return "F5E4-" + hashlib.sha1(target.encode("utf-8")).hexdigest()[:10].upper()


def classify(group):
    cases = group["cases"]
    repos = sorted({c["repo"] for c in cases})
    pages = sorted({(c["repo"], c["page_path"]) for c in cases})
    kinds = Counter(c.get("kind") for c in cases)
    count = len(cases)
    repo_count = len(repos)
    page_count = len(pages)

    # En esta etapa los fallos confirmados son de navegacion HTTP. No se eleva a
    # CRITICO sin evidencia de caida global, seguridad, datos o autenticacion.
    if repo_count >= 2 or count >= 4 or page_count >= 4:
        severity = "ALTO"
        priority = "P1_ALTA"
        rationale = "Fallo reproducible con alcance repetido o transversal; afecta navegacion disponible para usuarios en varias ubicaciones."
    else:
        severity = "MEDIO"
        priority = "P2_MEDIA"
        rationale = "Fallo reproducible y visible, pero localizado en una unica referencia o ubicacion de menor alcance."

    return {
        "severity": severity,
        "priority": priority,
        "rationale": rationale,
        "affected_repositories": repos,
        "affected_repository_count": repo_count,
        "affected_pages": [{"repo": r, "path": p} for r, p in pages],
        "affected_page_count": page_count,
        "case_count": count,
        "kinds": dict(kinds),
    }


def build(audit, output):
    output.mkdir(parents=True, exist_ok=True)
    failures = [r for r in audit.get("results", []) if r.get("stage_3_status") == "FALLO_CONFIRMADO"]
    grouped = defaultdict(list)
    for case in failures:
        evidence = case.get("stage_3_evidence") or {}
        target = evidence.get("final_url") or evidence.get("requested_url") or case.get("target") or case.get("page_url")
        grouped[target].append(case)

    findings = []
    for target, cases in grouped.items():
        info = classify({"cases": cases})
        http_statuses = sorted({(c.get("stage_3_evidence") or {}).get("http_status") for c in cases if (c.get("stage_3_evidence") or {}).get("http_status") is not None})
        labels = sorted({c.get("label") for c in cases if c.get("label")})
        finding = {
            "id": finding_id(target),
            "cause_key": target,
            "category": "NAVEGACION_DESTINO_NO_DISPONIBLE",
            "target": target,
            "evidence": {"http_statuses": http_statuses, "stage_3_status": "FALLO_CONFIRMADO"},
            "labels": labels,
            **info,
            "stage_4_status": "PRIORIZADO_PENDIENTE_DIAGNOSTICO",
            "correction_authorized": False,
        }
        findings.append(finding)

    priority_order = {"P0_CRITICA": 0, "P1_ALTA": 1, "P2_MEDIA": 2, "P3_BAJA": 3}
    findings.sort(key=lambda f: (priority_order[f["priority"]], -f["case_count"], f["target"]))
    total_cases = sum(f["case_count"] for f in findings)
    source_expected = audit.get("summary", {}).get("by_status", {}).get("FALLO_CONFIRMADO", len(failures))
    complete = bool(findings) and total_cases == len(failures) == source_expected

    result = {
        "manifest": {
            "phase": 5,
            "stage": 4,
            "name": "Clasificacion y priorizacion de hallazgos funcionales",
            "status": "completo" if complete else "incompleto",
            "source_stage": 3,
            "source_confirmed_failures": source_expected,
            "confirmed_failure_cases_grouped": total_cases,
            "unique_findings": len(findings),
            "mode": "analysis_only_no_correction",
            "limits": [
                "No modifica los ocho repositorios EVA.",
                "No corrige hallazgos.",
                "No convierte casos manuales o bloqueados en fallos.",
                "La severidad se asigna por impacto y alcance, no por cantidad bruta de casos solamente."
            ]
        },
        "summary": {
            "by_priority": dict(Counter(f["priority"] for f in findings)),
            "by_severity": dict(Counter(f["severity"] for f in findings))
        },
        "findings": findings
    }
    (output / "functional-prioritization.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Fase 5, Etapa 4: clasificacion y priorizacion de hallazgos funcionales",
        "",
        f"Estado: {'completo' if complete else 'incompleto'}.",
        "",
        f"Los {len(failures)} casos `FALLO_CONFIRMADO` de la Etapa 3 se agrupan en {len(findings)} hallazgos causales.",
        "",
        "| Orden | Prioridad | Severidad | Casos | Repositorios | Destino |",
        "|---:|---|---|---:|---:|---|"
    ]
    for i, f in enumerate(findings, 1):
        lines.append(f"| {i} | {f['priority']} | {f['severity']} | {f['case_count']} | {f['affected_repository_count']} | `{f['target']}` |")
    lines += [
        "",
        "Esta etapa no autoriza correcciones. Cada hallazgo queda `PRIORIZADO_PENDIENTE_DIAGNOSTICO` para la Etapa 5."
    ]
    (output / "Informe_fase_5_etapa_4.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return "completo" if complete else "incompleto", result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--audit", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("reports/functional-prioritization"))
    args = p.parse_args()
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    status, result = build(audit, args.output)
    print(f"Priorizacion funcional {status}: {len(result['findings'])} hallazgos")
    raise SystemExit(0 if status == "completo" else 1)


if __name__ == "__main__":
    main()
