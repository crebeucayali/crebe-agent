import unittest

import security_phase_validate as validator


class SecurityPhasePreparationTests(unittest.TestCase):
    def test_preparation_is_valid(self):
        self.assertEqual(validator.validate(), [])


if __name__ == "__main__":
    unittest.main()
