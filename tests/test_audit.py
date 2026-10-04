import tempfile
import unittest
from pathlib import Path
from audit import page_kind, audit, read
from visual_audit import allowed_request, evaluate


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = read('rules/consistency.json')

    def test_page_types_do_not_apply_public_rules_to_admin_or_auxiliary(self):
        for path, title, expected in [('admin.html', 'Panel', 'administrativa'), ('google123.html', '', 'auxiliar'), ('pruebas/index.html', '', 'auxiliar'), ('contacto.html', 'Redirigiendo', 'auxiliar'), ('index.html', 'Portada', 'portada'), ('recursos/galeria.html', 'Galería', 'publica')]:
            self.assertEqual(page_kind({'repo': 'accesos-complementarios', 'path': path, 'title': title}, self.rules), expected)

    def test_backend_and_writes_are_blocked(self):
        self.assertTrue(allowed_request('https://crebeucayali.github.io/index.html', 'GET'))
        self.assertFalse(allowed_request('https://crebeucayali.github.io/index.html', 'POST'))
        self.assertFalse(allowed_request('https://example.supabase.co/rest/v1/items', 'GET'))
        self.assertFalse(allowed_request('https://crebeucayali.github.io.evil.example/', 'GET'))

    def test_visual_sizes_use_viewport_specific_rules(self):
        page = {'repo': 'capacitaciones', 'viewport': 'mobile', 'http_status': 200, 'selectors': {'links': 'a'}, 'measurements': {'horizontal_overflow': 0, 'nav': {'minHeight': '74px'}, 'nav_links': [{'fontSize': '14px', 'fontWeight': '600'}], 'share_labels': ['Compartir']}}
        self.assertEqual(evaluate(page, self.rules), [])
        page['measurements']['nav_links'][0]['fontSize'] = '18px'
        self.assertEqual(evaluate(page, self.rules)[0]['rule'], 'navigation.font')

    def test_unverified_page_is_not_counted_as_consistent(self):
        result = evaluate({'repo': 'DUA-3.0', 'viewport': 'desktop', 'error': 'TimeoutError'}, self.rules)
        self.assertEqual(result[0]['level'], 'no_verificado')

    def test_cache_versions_do_not_create_code_inconsistencies(self):
        import json
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            components = {key: [{'line': 1}] for key in self.rules['home_required_components']}
            pages = []
            for query in ['v=8', 'v=9']:
                pages.append({'repo': 'crebeucayali.github.io', 'path': 'index.html', 'title': 'Inicio', 'components': components, 'images': [], 'references': [{'kind': 'script', 'line': 3, 'target_repo': 'crebeucayali.github.io', 'target_path': 'compartir-facebook.js', 'resolved_url': 'https://crebeucayali.github.io/compartir-facebook.js?' + query, 'query': query, 'target_content_sha256': 'same-code'}]})
            data = {'manifest.json': {'status': 'completo', 'captured_at': 'test'}, 'components.json': {'pages': pages}, 'repositories.json': [{'repo': 'crebeucayali.github.io', 'commit': 'commit', 'files': [{'path': 'compartir-facebook.js'}]}]}
            for name, content in data.items():
                (folder / name).write_text(json.dumps(content), encoding='utf-8')
            result = audit(folder, self.rules, folder / 'result')
            self.assertEqual(result['findings'], [])
            self.assertEqual(result['shared_script_variants'][0]['code_variants'], 1)
            pages[0]['references'][0]['target_path'] = 'missing.js'
            (folder / 'components.json').write_text(json.dumps({'pages': pages}), encoding='utf-8')
            result = audit(folder, self.rules, folder / 'result')
            self.assertEqual(result['findings'][0]['rule'], 'reference.exists')


if __name__ == '__main__':
    unittest.main()
