import tempfile
import unittest
from pathlib import Path

from functional_prioritization import build, classify, finding_id


class FunctionalPrioritizationTests(unittest.TestCase):
    def test_finding_id_is_stable(self):
        url = "https://example.test/missing"
        self.assertEqual(finding_id(url), finding_id(url))

    def test_repeated_cross_repo_failure_is_high(self):
        group = {"cases": [
            {"repo": "a", "page_path": "index.html", "kind": "navegacion"},
            {"repo": "b", "page_path": "index.html", "kind": "navegacion"},
        ]}
        result = classify(group)
        self.assertEqual(result["severity"], "ALTO")
        self.assertEqual(result["priority"], "P1_ALTA")

    def test_single_local_failure_is_medium(self):
        group = {"cases": [{"repo": "a", "page_path": "mapa.html", "kind": "navegacion"}]}
        result = classify(group)
        self.assertEqual(result["severity"], "MEDIO")
        self.assertEqual(result["priority"], "P2_MEDIA")

    def test_build_groups_cases_by_target(self):
        audit = {
            "summary": {"by_status": {"FALLO_CONFIRMADO": 3}},
            "results": [
                {"stage_3_status": "FALLO_CONFIRMADO", "repo": "a", "page_path": "1.html", "kind": "navegacion", "label": "A", "target": "/x", "stage_3_evidence": {"final_url": "https://x.test/", "http_status": 404}},
                {"stage_3_status": "FALLO_CONFIRMADO", "repo": "b", "page_path": "2.html", "kind": "navegacion", "label": "A", "target": "/x", "stage_3_evidence": {"final_url": "https://x.test/", "http_status": 404}},
                {"stage_3_status": "FALLO_CONFIRMADO", "repo": "a", "page_path": "3.html", "kind": "navegacion", "label": "B", "target": "/y", "stage_3_evidence": {"final_url": "https://y.test/", "http_status": 404}},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            status, result = build(audit, Path(tmp))
            self.assertEqual(status, "completo")
            self.assertEqual(len(result["findings"]), 2)
            self.assertEqual(sum(f["case_count"] for f in result["findings"]), 3)
            self.assertTrue((Path(tmp) / "functional-prioritization.json").exists())


if __name__ == "__main__":
    unittest.main()
