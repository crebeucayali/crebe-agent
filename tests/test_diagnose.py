import unittest
from diagnose import share_features, static_diagnosis


class DiagnosisTests(unittest.TestCase):
    def test_share_label_cause_requires_both_html_and_missing_normalization(self):
        snapshot = {'sources': [{'repo': 'DUA-3.0', 'path': 'index.html', 'sha': 'html', 'content': '<a>Compartir en Facebook</a>'}, {'repo': 'DUA-3.0', 'path': 'compartir-facebook.js', 'sha': 'js', 'content': 'navigator.share(datos);'}]}
        static = {'findings': [], 'shared_script_variants': []}
        visual = {'findings': [{'repo': 'DUA-3.0', 'rule': 'share.label'}]}
        case = static_diagnosis(snapshot, static, visual)[0]
        self.assertEqual(case['status'], 'causa_estatica_confirmada')
        snapshot['sources'][1]['content'] += ' enlace.textContent = "Compartir";'
        case = static_diagnosis(snapshot, static, visual)[0]
        self.assertEqual(case['status'], 'requiere_revision')

    def test_shared_scripts_are_grouped_without_assuming_a_defect(self):
        snapshot = {'sources': [{'repo': 'capacitaciones', 'path': 'compartir-facebook.js', 'sha': 'js', 'content': 'enlace.textContent="Compartir";'}]}
        ref = {'repo': 'capacitaciones', 'path': 'index.html', 'code_sha256': 'hash', 'target_repo': 'capacitaciones', 'target_path': 'compartir-facebook.js', 'cache_query': 'v=9'}
        static = {'findings': [], 'shared_script_variants': [{'script': 'compartir-facebook.js', 'references': [ref, dict(ref, path='recursos.html')]}]}
        cases = static_diagnosis(snapshot, static, {'findings': []})
        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0]['status'], 'variante_identificada')
        self.assertEqual(len(cases[0]['references']), 2)


if __name__ == '__main__':
    unittest.main()
