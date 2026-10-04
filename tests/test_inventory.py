import unittest
from inventory import Page, target_for, source_entry


class InventoryTests(unittest.TestCase):
    def test_cross_repo_and_encoded_paths(self):
        self.assertEqual(target_for('https://crebeucayali.github.io/DUA-3.0/compartir-facebook.js?v=9'), ('DUA-3.0', 'compartir-facebook.js'))
        self.assertEqual(target_for('https://crebeucayali.github.io/capacitaciones/'), ('capacitaciones', 'index.html'))
        self.assertEqual(target_for('https://crebeucayali.github.io/a%20b.css'), ('crebeucayali.github.io', 'a b.css'))
        self.assertIsNone(target_for('https://example.org/a.js'))

    def test_comments_not_parsed_as_elements(self):
        page = Page()
        page.feed('<!-- <header></header><script src="old.js"></script> --><footer class="pie"><a href="/">Inicio</a></footer><script src="new.js?v=3"></script>')
        self.assertEqual([e['tag'] for e in page.elements], ['footer'])
        self.assertEqual(page.refs[0]['value'], 'new.js?v=3')
        self.assertEqual(page.links[0]['text'], 'Inicio')

    def test_scan_exclusions(self):
        self.assertFalse(source_entry({'type': 'blob', 'path': 'vendor/a.js'}))
        self.assertFalse(source_entry({'type': 'blob', 'path': 'logo.png'}))
        self.assertTrue(source_entry({'type': 'blob', 'path': 'recursos/calendario.html'}))


if __name__ == '__main__':
    unittest.main()
