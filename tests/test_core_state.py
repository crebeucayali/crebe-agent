import json
import unittest
from pathlib import Path

from core.state import ROOT, build_current_state


class CurrentStateTests(unittest.TestCase):
    def test_repository_snapshot_matches_sources(self):
        expected = build_current_state(ROOT)
        current = json.loads((ROOT / "state" / "current.json").read_text(encoding="utf-8"))
        self.assertEqual(current, expected)

    def test_builder_keeps_legacy_sources_read_only(self):
        sources = [
            ROOT / "tracking" / "phases.json",
            ROOT / "tracking" / "fase-7-etapa-7.json",
            ROOT / "tracking" / "directorio-entidades-etapa-6.json",
            ROOT / "tracking" / "mapa-web-etapa-6.json",
        ]
        before = {path: path.read_bytes() for path in sources}
        state = build_current_state(ROOT)
        after = {path: path.read_bytes() for path in sources}
        self.assertEqual(before, after)
        self.assertTrue(state["guardrails"]["legacy_tracking_preserved"])
        self.assertFalse(state["guardrails"]["legacy_tracking_modified_by_builder"])

    def test_current_state_covers_existing_operational_domains(self):
        state = build_current_state(ROOT)
        self.assertEqual(
            set(state["phases"]),
            {"fase_4", "fase_5", "fase_6", "fase_7", "fase_8"},
        )
        self.assertEqual(
            set(state["modules"]),
            {"directory_entities", "mapa_web"},
        )
        self.assertEqual(state["canonical_path"], "state/current.json")

    def test_security_authentication_is_projected_into_current_state(self):
        state = build_current_state(ROOT)
        phase = state["phases"]["fase_7"]
        self.assertEqual(phase["detail_source"], "tracking/fase-7-etapa-7.json")
        self.assertEqual(
            phase["authentication"]["master"],
            "AUTHENTICATED_PLUS_AAL2_MFA",
        )
        self.assertFalse(phase["authentication"]["mfa_obligatorio_editores"])

    def test_mapa_web_stage_6_is_projected_into_current_state(self):
        state = build_current_state(ROOT)
        module = state["modules"]["mapa_web"]
        self.assertEqual(module["stage"], 6)
        self.assertEqual(module["status"], "ACTUALIZACION_CONTROLADA_MAPA_WEB_COMPLETADA")
        self.assertEqual(module["source"], "tracking/mapa-web-etapa-6.json")


if __name__ == "__main__":
    unittest.main()
