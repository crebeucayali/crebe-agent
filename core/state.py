from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CURRENT_STATE = ROOT / "state" / "current.json"
PHASES = ROOT / "tracking" / "phases.json"
SECURITY_STAGE_7 = ROOT / "tracking" / "fase-7-etapa-7.json"
DIRECTORY_ENTITIES = ROOT / "tracking" / "directorio-entidades-etapa-6.json"
MAPA_WEB = ROOT / "tracking" / "mapa-web-etapa-5.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_current_state(root: Path = ROOT) -> dict[str, Any]:
    phases_path = root / "tracking" / "phases.json"
    security_stage_7_path = root / "tracking" / "fase-7-etapa-7.json"
    directory_path = root / "tracking" / "directorio-entidades-etapa-6.json"
    mapa_path = root / "tracking" / "mapa-web-etapa-5.json"

    phases = read_json(phases_path)
    security_stage_7 = read_json(security_stage_7_path)
    directory = read_json(directory_path)
    mapa = read_json(mapa_path)

    phase_state: dict[str, Any] = {}
    for key, value in phases.items():
        if not key.startswith("fase_") or not isinstance(value, dict):
            continue
        phase_state[key] = {
            "status": value.get("estado"),
            "current_stage": value.get("etapa_actual"),
            "source": "tracking/phases.json",
        }

    if "fase_7" in phase_state:
        phase_state["fase_7"]["authentication"] = security_stage_7.get(
            "modelo_autenticacion_confirmado", {}
        )
        phase_state["fase_7"]["detail_source"] = "tracking/fase-7-etapa-7.json"

    return {
        "schema_version": 1,
        "kind": "CREBE_AGENT_CURRENT_STATE",
        "mode": "TRANSITIONAL_CANONICAL_VIEW",
        "canonical_path": "state/current.json",
        "sources": [
            "tracking/phases.json",
            "tracking/fase-7-etapa-7.json",
            "tracking/directorio-entidades-etapa-6.json",
            "tracking/mapa-web-etapa-5.json",
        ],
        "phases": phase_state,
        "modules": {
            "directory_entities": {
                "status": directory.get("estado"),
                "stage": directory.get("etapa"),
                "mode": directory.get("modo"),
                "source": "tracking/directorio-entidades-etapa-6.json",
            },
            "mapa_web": {
                "status": mapa.get("status"),
                "stage": mapa.get("stage"),
                "scope": mapa.get("scope"),
                "source": "tracking/mapa-web-etapa-5.json",
            },
        },
        "guardrails": {
            "legacy_tracking_preserved": True,
            "legacy_tracking_modified_by_builder": False,
            "existing_modules_moved": False,
            "existing_modules_deleted": False,
            "eva_repositories_modified": False,
            "supabase_modified": False,
        },
    }


def refresh_current_state(root: Path = ROOT) -> dict[str, Any]:
    state = build_current_state(root)
    write_json(root / "state" / "current.json", state)
    return state


if __name__ == "__main__":
    refresh_current_state()
    print("state/current.json actualizado desde tracking legado sin modificar sus fuentes")
