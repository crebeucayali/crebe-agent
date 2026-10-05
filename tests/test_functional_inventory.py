import unittest

from functional_inventory import FunctionalParser, classify_href, expected_behavior


class FunctionalInventoryTests(unittest.TestCase):
    def test_classify_href(self):
        self.assertEqual(classify_href("#agenda"), "ancla_interna")
        self.assertEqual(classify_href("mailto:crebe@example.org"), "correo")
        self.assertEqual(classify_href("https://drive.google.com/file/d/x"), "enlace_externo")
        self.assertEqual(classify_href("recursos/material.pdf"), "navegacion")

    def test_parser_collects_interactive_elements(self):
        parser = FunctionalParser()
        parser.feed('''
        <a id="material" href="https://drive.google.com/file/d/x">Abrir material</a>
        <button id="share" type="button">Compartir</button>
        <form id="news" method="post" action="/api/news">
          <input name="title" required>
          <select name="level"><option>Inicial</option></select>
        </form>
        <iframe src="https://www.youtube.com/embed/x"></iframe>
        ''')
        kinds = [item["kind"] for item in parser.elements]
        self.assertIn("enlace_externo", kinds)
        self.assertIn("boton", kinds)
        self.assertIn("formulario", kinds)
        self.assertIn("control_formulario", kinds)
        self.assertIn("recurso_embebido", kinds)
        form_controls = [item for item in parser.elements if item["kind"] == "control_formulario"]
        self.assertTrue(all(item.get("form_line") for item in form_controls))

    def test_expected_link_behavior_resolves_relative_target(self):
        behavior = expected_behavior(
            {"kind": "navegacion", "target": "recursos/material.html"},
            "https://crebeucayali.github.io/capacitaciones/index.html",
        )
        self.assertEqual(behavior["action"], "activar_enlace")
        self.assertEqual(
            behavior["resolved_target"],
            "https://crebeucayali.github.io/capacitaciones/recursos/material.html",
        )


if __name__ == "__main__":
    unittest.main()
