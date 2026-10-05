"""Fase 5, Etapa 2: casos de prueba y resultados esperados de EVA.

Consume el inventario funcional de la Etapa 1 y genera un caso por elemento.
No ejecuta acciones sobre EVA, no consulta Supabase y no modifica repositorios EVA.
"""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

CRITICAL_LABELS = re.compile(
    r"\b(guardar|publicar|eliminar|borrar|subir|crear|iniciar sesi[oó]n|login|cerrar sesi[oó]n|mfa|2fa|administrar|admin)\b",
    re.I,
)
HIGH_LABELS = re.compile(
    r"\b(compartir|calendario|capacitaci[oó]n|material|noticia|galer[ií]a|repositorio|descargar|abrir|ver|acceder)\b",
    re.I,
)


def stable_id(repo, path, element):
    raw = "|".join([
        repo,
        path,
        str(element.get("line", "")),
        element.get("kind", ""),
        element.get("label", ""),
        element.get("target", ""),
    ])
    return "F5E2-" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12].upper()


def priority_for(scope, element):
    label = element.get("label", "")
    kind = element.get("kind", "")
    if scope == "administrativo" and (kind in {"formulario", "boton", "control_formulario"} or CRITICAL_LABELS.search(label)):
        return "P0_CRITICA"
    if kind == "formulario" or CRITICAL_LABELS.search(label):
        return "P1_ALTA"
    if kind in {"boton", "recurso_embebido"} or HIGH_LABELS.search(label):
        return "P1_ALTA"
    if kind in {"navegacion", "enlace_externo"}:
        return "P2_MEDIA"
    return "P3_BAJA"


def execution_policy(scope, element):
    kind = element.get("kind", "")
    if scope == "administrativo" and kind in {"formulario", "boton", "control_formulario"}:
        return "SESION_CONTROLADA_DATOS_PRUEBA"
    if kind == "formulario":
        return "DATOS_PRUEBA_CONTROLADOS"
    if kind in {"correo", "telefono", "javascript_inline"}:
        return "MANUAL_O_INSTRUMENTADA"
    if kind == "enlace_externo":
        return "LECTURA_SIN_EFECTOS_EXTERNOS"
    if kind in {"navegacion", "ancla_interna", "recurso_embebido"}:
        return "AUTOMATIZABLE_LECTURA"
    if kind == "boton":
        return "NAVEGADOR_INSTRUMENTADO_SIN_PERSISTENCIA"
    if kind == "control_formulario":
        return "NAVEGADOR_INSTRUMENTADO_SIN_ENVIO"
    return "REVISION_CONTROLADA"


def expected_for(page, element):
    kind = element.get("kind", "")
    target = element.get("expected_behavior", {}).get("resolved_target")
    label = element.get("label") or element.get("id") or element.get("name") or kind
    if kind == "navegacion":
        return {
            "action": f"Activar el enlace '{label}'.",
            "expected": "La navegación llega al destino previsto sin 404, error de carga ni redirección inesperada.",
            "evidence": ["URL final", "estado HTTP o carga del documento", "ausencia de error visible"],
        }
    if kind == "enlace_externo":
        return {
            "action": f"Validar el enlace externo '{label}' sin ejecutar acciones en el servicio de destino.",
            "expected": "El destino está bien formado y es alcanzable; EVA no apunta a una ruta inexistente o claramente incorrecta.",
            "evidence": ["URL resuelta", "respuesta de lectura cuando sea segura"],
        }
    if kind == "ancla_interna":
        return {
            "action": f"Activar el ancla '{label}'.",
            "expected": "La página desplaza o enfoca el elemento interno correspondiente sin perder el contexto.",
            "evidence": ["fragmento de URL", "elemento objetivo existente"],
        }
    if kind == "recurso_embebido":
        return {
            "action": f"Cargar el recurso embebido asociado a '{label}'.",
            "expected": "El recurso se carga sin error y permanece disponible en el contexto de la página.",
            "evidence": ["solicitud del recurso", "estado de carga", "ausencia de recurso roto"],
        }
    if kind == "formulario":
        return {
            "action": f"Completar el formulario '{label}' con datos de prueba válidos y enviarlo solo en entorno controlado.",
            "expected": "Las validaciones se respetan y el envío produce la respuesta prevista por su action/method sin duplicados ni errores inesperados.",
            "evidence": ["validación de campos", "respuesta del envío", "estado visible posterior", "efecto persistente solo si está autorizado"],
        }
    if kind == "control_formulario":
        required = element.get("required", False)
        return {
            "action": f"Interactuar con el control '{label}'.",
            "expected": "El control acepta o selecciona un valor válido" + (" y aplica su obligatoriedad" if required else "") + ".",
            "evidence": ["valor del control", "estado de validación", "accesibilidad del foco"],
        }
    if kind == "boton":
        return {
            "action": f"Activar el botón '{label}' en navegador instrumentado.",
            "expected": "El botón ejecuta una acción observable coherente con su etiqueta o manejador, sin error JavaScript ni efecto lateral no autorizado.",
            "evidence": ["evento asociado", "cambio visible o navegación", "errores de consola", "solicitudes generadas"],
        }
    if kind == "correo":
        return {"action": f"Validar el enlace de correo '{label}'.", "expected": "El esquema mailto y el destinatario están correctamente formados.", "evidence": ["href mailto"]}
    if kind == "telefono":
        return {"action": f"Validar el enlace telefónico '{label}'.", "expected": "El esquema tel y el número están correctamente formados.", "evidence": ["href tel"]}
    if kind == "javascript_inline":
        return {"action": f"Revisar la acción JavaScript inline '{label}'.", "expected": "La acción se ejecuta sin error y produce únicamente el efecto previsto.", "evidence": ["handler inline", "errores de consola", "efecto observable"]}
    return {"action": f"Revisar '{label}'.", "expected": "El elemento responde de acuerdo con su función declarada.", "evidence": ["resultado observable"]}


def risk_notes(scope, element):
    notes = []
    kind = element.get("kind", "")
    if scope == "administrativo":
        notes.append("Puede requerir autenticación y no debe probarse con credenciales o datos productivos fuera de una sesión controlada.")
    if kind == "formulario":
        notes.append("El envío puede generar persistencia; usar datos de prueba y verificar duplicados.")
    target = element.get("expected_behavior", {}).get("resolved_target") or ""
    host = urlsplit(target).netloc
    if host and host not in {"crebeucayali.github.io"}:
        notes.append("Destino externo: limitar la prueba a lectura cuando sea posible.")
    return notes


def build(inventory, output):
    output.mkdir(parents=True, exist_ok=True)
    cases = []
    priorities = Counter()
    policies = Counter()
    kinds = Counter()
    repos = Counter()

    for page in inventory.get("pages", []):
        repo, path, scope = page["repo"], page["path"], page["scope"]
        for element in page.get("functional_elements", []):
            case_id = stable_id(repo, path, element)
            priority = priority_for(scope, element)
            policy = execution_policy(scope, element)
            expected = expected_for(page, element)
            case = {
                "id": case_id,
                "repo": repo,
                "page_path": path,
                "page_url": page.get("url_expected"),
                "page_sha": page.get("sha"),
                "scope": scope,
                "source_line": element.get("line"),
                "kind": element.get("kind"),
                "label": element.get("label"),
                "target": element.get("target"),
                "priority": priority,
                "execution_policy": policy,
                "action": expected["action"],
                "expected_result": expected["expected"],
                "evidence_required": expected["evidence"],
                "risk_notes": risk_notes(scope, element),
                "stage_2_status": "DEFINIDO_NO_EJECUTADO",
            }
            cases.append(case)
            priorities[priority] += 1
            policies[policy] += 1
            kinds[case["kind"]] += 1
            repos[repo] += 1

    duplicate_ids = len(cases) - len({c["id"] for c in cases})
    source_total = sum(len(p.get("functional_elements", [])) for p in inventory.get("pages", []))
    expected_repos = set(inventory.get("manifest", {}).get("repositories", []))
    represented = set(repos)
    status = "completo" if cases and not duplicate_ids and len(cases) == source_total and represented.issuperset(expected_repos) else "incompleto"
    manifest = {
        "phase": 5,
        "stage": 2,
        "name": "Casos de prueba y resultados esperados",
        "status": status,
        "mode": "definition_only_no_execution",
        "source_stage": 1,
        "source_cases_expected": source_total,
        "generated_cases": len(cases),
        "duplicate_ids": duplicate_ids,
        "repositories_expected": sorted(expected_repos),
        "repositories_represented": sorted(represented),
        "limits": [
            "No se ejecuta ningún caso de prueba.",
            "No se pulsa ningún botón ni enlace.",
            "No se envían formularios.",
            "No se consulta ni modifica Supabase.",
            "No se modifican los ocho repositorios EVA.",
            "La prioridad organiza el orden de ejecución; no declara que exista un fallo.",
        ],
    }
    result = {
        "manifest": manifest,
        "summary": {
            "by_priority": dict(priorities),
            "by_execution_policy": dict(policies),
            "by_kind": dict(kinds),
            "by_repo": dict(repos),
        },
        "test_cases": cases,
    }
    (output / "functional-test-cases.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    ordered_priorities = ["P0_CRITICA", "P1_ALTA", "P2_MEDIA", "P3_BAJA"]
    report = [
        "# Fase 5, Etapa 2: casos de prueba y resultados esperados",
        "",
        f"Estado: {status}.",
        "",
        f"Casos definidos: {len(cases)}. Cada elemento funcional de la Etapa 1 conserva un caso trazable y permanece en estado `DEFINIDO_NO_EJECUTADO`.",
        "",
        "| Prioridad | Casos | Criterio |",
        "|---|---:|---|",
        f"| P0_CRITICA | {priorities['P0_CRITICA']} | Acciones administrativas o potencialmente persistentes. |",
        f"| P1_ALTA | {priorities['P1_ALTA']} | Formularios, botones, recursos y funciones principales. |",
        f"| P2_MEDIA | {priorities['P2_MEDIA']} | Navegación interna o externa relevante. |",
        f"| P3_BAJA | {priorities['P3_BAJA']} | Anclas, correo, teléfono y controles de menor impacto. |",
        "",
        "Política de ejecución: las acciones administrativas y formularios que puedan persistir datos se reservan para sesión controlada y datos de prueba. La navegación y carga de recursos podrán automatizarse en modo lectura cuando corresponda. Los destinos externos se limitan a validaciones sin efectos laterales.",
        "",
        "Esta etapa no demuestra funcionamiento correcto ni detecta fallos. Su producto es el contrato de prueba que utilizará la Etapa 3 para ejecutar la auditoría funcional inicial y registrar CORRECTO, FALLO_CONFIRMADO, REQUIERE_VERIFICACION_MANUAL, NO_APLICA o BLOQUEADO_POR_DEPENDENCIA.",
    ]
    (output / "Informe_fase_5_etapa_2.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return status, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True, help="functional-inventory.json producido por la Etapa 1")
    parser.add_argument("--output", type=Path, default=Path("reports/functional-test-cases"))
    args = parser.parse_args()
    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    status, result = build(inventory, args.output)
    print(f"Casos funcionales {status}: {len(result['test_cases'])}")
    raise SystemExit(0 if status == "completo" else 1)


if __name__ == "__main__":
    main()
