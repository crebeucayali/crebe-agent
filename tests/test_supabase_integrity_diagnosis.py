import unittest
from supabase_integrity_diagnosis_validate import validate


class DiagnosisTests(unittest.TestCase):
    def test_clean_diagnosis_passes(self):
        data = {
            "fase": 6,
            "etapa": 6,
            "estado": "ETAPA_6_COMPLETADA_DIAGNOSTICO_INTEGRIDAD",
            "resultado": {
                "inconsistencias_confirmadas": 0,
                "hallazgos_diagnosticables": 0,
                "hallazgos_que_requieren_correccion": 0,
                "storage_candidatos_revision": 24,
                "dependencias_seguridad": 1,
                "correccion_autorizada": False,
                "supabase_modificado": False,
                "repositorios_eva_modificados": False,
            },
            "separaciones": [
                {"id": "STORAGE-CANDIDATES-001"},
                {"id": "SEC-DEPENDENCY-001"},
            ],
            "etapa_7_requerida_por_hallazgos_actuales": False,
        }
        self.assertTrue(validate(data))

    def test_no_correction_can_be_authorized_without_findings(self):
        data = {
            "fase": 6,
            "etapa": 6,
            "estado": "ETAPA_6_COMPLETADA_DIAGNOSTICO_INTEGRIDAD",
            "resultado": {
                "inconsistencias_confirmadas": 0,
                "hallazgos_diagnosticables": 0,
                "hallazgos_que_requieren_correccion": 0,
                "storage_candidatos_revision": 24,
                "dependencias_seguridad": 1,
                "correccion_autorizada": True,
                "supabase_modificado": False,
                "repositorios_eva_modificados": False,
            },
            "separaciones": [
                {"id": "STORAGE-CANDIDATES-001"},
                {"id": "SEC-DEPENDENCY-001"},
            ],
            "etapa_7_requerida_por_hallazgos_actuales": False,
        }
        with self.assertRaises(AssertionError):
            validate(data)


if __name__ == "__main__":
    unittest.main()
