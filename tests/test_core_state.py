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
            ROOT / "tracking" / "directorio-entidades-etapa-6.json",
            ROOT / "tracking" / "mapa-web-etapa-5.json",
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


if __name__ == "__main__":
    unittest.main()
