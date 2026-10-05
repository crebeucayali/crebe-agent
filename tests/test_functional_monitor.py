import unittest
from unittest.mock import patch

import functional_monitor


class FunctionalMonitorTests(unittest.TestCase):
    def test_evaluate_accepts_success(self):
        target = {"allowed_statuses": [200], "must_contain": ["ok"], "must_not_contain": ["old"]}
        status, _ = functional_monitor.evaluate(target, {"status": 200, "body": "ok current"})
        self.assertEqual(status, "CORRECTO")

    def test_evaluate_flags_http_failure(self):
        status, detail = functional_monitor.evaluate({}, {"status": 404, "body": ""})
        self.assertEqual(status, "ALERTA")
        self.assertIn("404", detail)

    def test_evaluate_flags_missing_marker(self):
        target = {"must_contain": ["expected"]}
        status, _ = functional_monitor.evaluate(target, {"status": 200, "body": "other"})
        self.assertEqual(status, "ALERTA")

    def test_evaluate_flags_forbidden_marker(self):
        target = {"must_not_contain": ["old-route"]}
        status, _ = functional_monitor.evaluate(target, {"status": 200, "body": "contains old-route"})
        self.assertEqual(status, "ALERTA")

    @patch("functional_monitor.request_url")
    def test_run_keeps_known_exception_outside_alert_count(self, request_url):
        request_url.return_value = {"status": 200, "final_url": "https://example.test/", "body": "ok", "error": None}
        config = {
            "targets": [{"id": "a", "name": "A", "url": "https://example.test/"}],
            "known_exceptions": [{"id": "known", "reason": "known"}],
        }
        result = functional_monitor.run(config)
        self.assertEqual(result["summary"]["correct"], 1)
        self.assertEqual(result["summary"]["alerts"], 0)
        self.assertEqual(result["summary"]["known_exceptions"], 1)


if __name__ == "__main__":
    unittest.main()
