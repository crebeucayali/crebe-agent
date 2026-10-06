import unittest

from supabase_integrity_controlled_writes_validate import validate_report


class ControlledWritesValidationTests(unittest.TestCase):
    def base(self):
        return {
            "estado": "ETAPA_5_COMPLETADA_PRUEBAS_CONTROLADAS",
            "modo": "CONTROLLED_TRANSACTION_ROLLBACK",
            "resultado_final": {
                "calendario_insert_update_ok": True,
                "capacitacion_insert_update_ok": True,
                "noticia_insert_update_ok": True,
                "galeria_padre_ok": True,
                "galeria_hija_ok": True,
                "galeria_on_delete_cascade_ok": True,
                "repositorio_insert_update_ok": True,
                "visitas_global_trigger_ok": True,
                "visitas_modulo_trigger_ok": True,
                "compartidos_trigger_ok": True,
                "visitas_eventos_efimeros_ok": True,
                "compartidos_eventos_efimeros_ok": True,
            },
            "rollback": {
                "ejecutado": True,
                "residuos_calendario": 0,
                "residuos_capacitaciones": 0,
            },
            "supabase_modificado_durablemente": False,
            "repositorios_eva_modificados": False,
            "hallazgos_confirmados": 0,
        }

    def test_valid_report(self):
        self.assertEqual(validate_report(self.base()), [])

    def test_failed_check_is_rejected(self):
        data = self.base()
        data["resultado_final"]["compartidos_trigger_ok"] = False
        self.assertTrue(validate_report(data))

    def test_residue_is_rejected(self):
        data = self.base()
        data["rollback"]["residuos_calendario"] = 1
        self.assertTrue(validate_report(data))

    def test_durable_mutation_is_rejected(self):
        data = self.base()
        data["supabase_modificado_durablemente"] = True
        self.assertTrue(validate_report(data))


if __name__ == "__main__":
    unittest.main()
