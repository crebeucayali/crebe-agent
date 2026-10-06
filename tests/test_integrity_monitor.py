import unittest
from unittest.mock import patch

import integrity_monitor as monitor


class IntegrityMonitorTests(unittest.TestCase):
    def fixture_rows(self):
        return {
            "calendario_actividades": [{"id": 1}, {"id": 2}],
            "capacitaciones_sesiones": [{"id": 10}],
            "calendario_publico": [
                {"registro_id": "actividad-1"},
                {"registro_id": "actividad-2"},
                {"registro_id": "capacitacion-10"},
            ],
            "noticias_destacadas": [{"id": 1, "imagen_url": "https://example.test/a.webp"}],
            "galeria_items": [{"id": 5, "imagen_url": ""}],
            "galeria_item_imagenes": [{"galeria_item_id": 5, "imagen_url": ""}],
            "repositorio_recursos": [{"id": 7, "imagen_url": ""}],
        }

    def run_with(self, rows, storage_result=True):
        def fake_rest(_base, _key, table, _params):
            return rows[table]

        with patch.object(monitor, "discover_public_config", return_value=("https://dteimbhwtzghhsijeeld.supabase.co", "sb_publishable_test")), \
             patch.object(monitor, "rest_rows", side_effect=fake_rest), \
             patch.object(monitor, "storage_ok", return_value=storage_result):
            return monitor.run_monitor()

    def test_healthy_monitor(self):
        report = self.run_with(self.fixture_rows())
        self.assertEqual(report["estado"], "OK")
        self.assertEqual(report["alertas"], [])

    def test_calendar_union_alert(self):
        rows = self.fixture_rows()
        rows["calendario_publico"] = rows["calendario_publico"][:-1]
        report = self.run_with(rows)
        ids = {a["id"] for a in report["alertas"]}
        self.assertIn("MON-CAL-001", ids)
        self.assertIn("MON-CAP-001", ids)

    def test_gallery_orphan_alert(self):
        rows = self.fixture_rows()
        rows["galeria_item_imagenes"] = [{"galeria_item_id": 999, "imagen_url": ""}]
        report = self.run_with(rows)
        self.assertIn("MON-GAL-001", {a["id"] for a in report["alertas"]})

    def test_storage_missing_alert(self):
        rows = self.fixture_rows()
        rows["noticias_destacadas"] = [{"id": 1, "imagen_url": "https://dteimbhwtzghhsijeeld.supabase.co/storage/v1/object/public/eva-publico/noticias/a.webp"}]
        report = self.run_with(rows, storage_result=False)
        self.assertIn("MON-STO-001", {a["id"] for a in report["alertas"]})


if __name__ == "__main__":
    unittest.main()
