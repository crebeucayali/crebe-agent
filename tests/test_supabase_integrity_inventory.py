import copy
import json
import unittest
from pathlib import Path

from supabase_integrity_inventory_validate import validate


class SupabaseIntegrityInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = json.loads(Path("baselines/fase-6-etapa-1-inventario.json").read_text(encoding="utf-8"))

    def test_committed_inventory_is_valid(self):
        self.assertEqual(validate(self.inventory), [])

    def test_calendar_projection_must_balance(self):
        data = copy.deepcopy(self.inventory)
        for item in data["objects"]:
            if item["name"] == "public.calendario_publico":
                item["rows"] += 1
        self.assertTrue(any("calendario_publico" in e for e in validate(data)))

    def test_storage_prefixes_must_balance(self):
        data = copy.deepcopy(self.inventory)
        for item in data["objects"]:
            if item["name"] == "storage:eva-publico":
                item["objects"] += 1
        self.assertTrue(any("Storage" in e for e in validate(data)))

    def test_inventory_must_remain_read_only(self):
        data = copy.deepcopy(self.inventory)
        data["mode"] = "WRITE"
        self.assertTrue(any("READ_ONLY" in e for e in validate(data)))


if __name__ == "__main__":
    unittest.main()
