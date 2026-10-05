"""Fase 5, Etapa 5: diagnostico tecnico de hallazgos funcionales.

Consume la priorizacion de la Etapa 4 y evidencia diagnostica verificada.
No modifica EVA ni aplica correcciones.
"""
import argparse
import json
from collections import Counter
from pathlib import Path


def build(prioritization, evidence, output):
    output.mkdir(parents=True, exist_ok=True)
    findings = prioritization.get("findings", [])
    diagnoses = evidence.get("diagnoses", {})
    results = []
    missing = []

    for finding in findings:
        fid = finding["id"]
        spec = diagnoses.get(fid)
        if not spec:
            missing.append(fid)
            continue
        correct_target = spec.get("correct_target")
        decision_required = spec.get("decision_required")
        status = (
            "DIAGNOSTICADO_LISTO_PARA_CORRECCION"
            if correct_target
            else "DIAGNOSTICADO_REQUIERE_DECISION_FUNCIONAL"
        )
        if not correct_target and not decision_required:
            missing.append(fid)
            continue
        results.append({
            "id": fid,
            "target_broken": finding.get("target"),
            "priority": finding.get("priority"),
            "severity": finding.get("severity"),
            "case_count": finding.get("case_count"),
            "affected_repositories": finding.get("affected_repositories", []),
            "affected_pages": finding.get("affected_pages", []),
            "root_cause": spec["root_cause"],
            "diagnosis": spec["diagnosis"],
            "correct_target": correct_target,
            "confidence": spec.get("confidence", "NO_DEFINIDA"),
            "technical_action_class": spec["technical_action_class"],
            "evidence": spec.get("evidence", []),
            "decision_required": decision_required,
            "stage_5_status": status,
            "correction_authorized": False,
        })

    source_ids = {f["id"] for f in findings}
    result_ids = {r["id"] for r in results}
    extra_evidence = sorted(set(diagnoses) - source_ids)
    complete = bool(findings) and source_ids == result_ids and not missing and not extra_evidence

    result = {
        "manifest": {
            "phase": 5,
            "stage": 5,
            "name": "Diagnostico tecnico de hallazgos funcionales",
            "status": "completo" if complete else "incompleto",
            "source_stage": 4,
            "source_findings": len(findings),
            "diagnosed_findings": len(results),
            "missing_diagnoses": sorted(missing),
            "extra_evidence_ids": extra_evidence,
            "mode": "diagnosis_only_no_correction",
            "limits": [
                "No modifica los ocho repositorios EVA.",
                "No corrige enlaces ni crea redirecciones.",
                "No inventa un destino cuando no existe evidencia de reemplazo vigente.",
                "La Etapa 6 requiere autorizacion separada para intervenir EVA."
            ]
        },
        "summary": {
            "by_status": dict(Counter(r["stage_5_status"] for r in results)),
            "by_root_cause": dict(Counter(r["root_cause"] for r in results)),
            "by_action_class": dict(Counter(r["technical_action_class"] for r in results)),
        },
        "diagnoses": results,
    }
    (output / "functional-diagnosis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Fase 5, Etapa 5: diagnostico tecnico de hallazgos funcionales",
        "",
        f"Estado: {'completo' if complete else 'incompleto'}.",
        "",
        f"Hallazgos diagnosticados: {len(results)} de {len(findings)}.",
        "",
        "| Prioridad | Hallazgo | Causa raiz | Destino correcto | Estado |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        target = r["correct_target"] or "Pendiente de decision funcional"
        lines.append(f"| {r['priority']} | `{r['id']}` | {r['root_cause']} | `{target}` | {r['stage_5_status']} |")
    lines += [
        "",
        "La Etapa 5 identifica causa y alcance tecnico; no aplica correcciones. Los archivos a intervenir se derivan de `affected_pages` de cada hallazgo.",
    ]
    (output / "Informe_fase_5_etapa_5.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return "completo" if complete else "incompleto", result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--prioritization", type=Path, required=True)
    p.add_argument("--evidence", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("reports/functional-diagnosis"))
    args = p.parse_args()
    prioritization = json.loads(args.prioritization.read_text(encoding="utf-8"))
    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    status, result = build(prioritization, evidence, args.output)
    print(f"Diagnostico funcional {status}: {len(result['diagnoses'])} hallazgos")
    raise SystemExit(0 if status == "completo" else 1)


if __name__ == "__main__":
    main()
