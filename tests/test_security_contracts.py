import json
import unittest
from pathlib import Path

import security_contracts_validate as validator

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts" / "fase-7-etapa-2-contratos-seguridad.json"


class SecurityContractsTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(CONTRACTS.read_text(encoding="utf-8"))

    def test_contracts_validate(self):
        self.assertEqual(validator.validate(), [])

    def test_all_six_surfaces_are_covered(self):
        self.assertEqual(
            set(self.data["superficies_cubiertas"]),
            {f"SEC-SURFACE-00{i}" for i in range(1, 7)},
        )

    def test_contract_ids_are_unique(self):
        ids = [c["id"] for c in self.data["contratos"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_no_correction_is_authorized(self):
        self.assertFalse(self.data["correccion_autorizada"])
        self.assertFalse(self.data["supabase_modificado"])
        self.assertFalse(self.data["repositorios_eva_modificados"])

    def test_service_role_stays_server_side(self):
        text = json.dumps(self.data, ensure_ascii=False)
        self.assertIn("service_role_no_debe_aparecer_en_cliente", text)

    def test_data_api_deadline_has_contract(self):
        self.assertTrue(any(c["id"] == "SEC-CON-026" for c in self.data["contratos"]))


if __name__ == "__main__":
    unittest.main()
