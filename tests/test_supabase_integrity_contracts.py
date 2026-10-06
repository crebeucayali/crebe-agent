import unittest

from supabase_integrity_contracts_validate import load_contracts, summary, validate_contracts


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_contracts()

    def test_contracts_are_valid(self):
        self.assertEqual(validate_contracts(self.data), [])

    def test_all_eight_modules_are_present(self):
        self.assertEqual(summary(self.data)["modules"], 8)

    def test_no_write_or_auto_correction(self):
        self.assertFalse(self.data["escritura_habilitada"])
        self.assertFalse(self.data["correccion_automatica"])

    def test_calendar_contract_is_dynamic_not_fixed_count(self):
        calendar = next(m for m in self.data["modulos"] if m["id"] == "calendario")
        rule = next(c for c in calendar["contratos"] if c["id"] == "CAL-002")
        self.assertIn("sin exigir un conteo fijo", rule["descripcion"])

    def test_ephemeral_event_contracts_exist(self):
        ids = {c["id"] for m in self.data["modulos"] for c in m["contratos"]}
        self.assertIn("VIS-001", ids)
        self.assertIn("COM-001", ids)

    def test_storage_reference_contract_exists(self):
        ids = {c["id"] for m in self.data["modulos"] for c in m["contratos"]}
        self.assertIn("STO-003", ids)


if __name__ == "__main__":
    unittest.main()
