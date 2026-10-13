import test from 'node:test';
import assert from 'node:assert/strict';
import { h1Texts, inspectContent, visibleText } from '../seo_content_verify.mjs';

test('h1Texts obtiene el encabezado principal visible', () => {
  assert.deepEqual(h1Texts('<main><h1>Educación <span>inclusiva</span></h1></main>'), ['Educación inclusiva']);
});

test('inspectContent aprueba una página oficial con un H1 y contenido suficiente', () => {
  const html = '<html><body><h1>Accesibilidad educativa</h1><p>' + 'Contenido sobre accesibilidad e inclusión educativa. '.repeat(5) + '</p></body></html>';
  const result = inspectContent('repo', 'https://crebeucayali.github.io/repo/', 'index.html', html);
  assert.equal(result.status, 'PASS');
  assert.equal(result.h1_count, 1);
  assert.ok(result.visible_text_chars >= 120);
  assert.ok(result.semantic_terms.length > 0);
});

test('inspectContent detecta H1 faltante o múltiple', () => {
  const base = '<p>' + 'Accesibilidad e inclusión educativa. '.repeat(8) + '</p>';
  const missing = inspectContent('repo', 'https://crebeucayali.github.io/repo/a', 'a.html', base);
  const multiple = inspectContent('repo', 'https://crebeucayali.github.io/repo/b', 'b.html', `<h1>Uno</h1><h1>Dos</h1>${base}`);
  assert.ok(missing.errors.includes('missing_h1'));
  assert.ok(multiple.errors.includes('multiple_h1'));
});

test('inspectContent detecta contenido insuficiente y ausencia de términos semánticos', () => {
  const result = inspectContent('repo', 'https://crebeucayali.github.io/repo/', 'index.html', '<h1>Página breve</h1><p>Texto general.</p>');
  assert.ok(result.errors.includes('thin_visible_content'));
  assert.ok(result.errors.includes('missing_semantic_terms'));
  assert.ok(visibleText('<style>x{}</style><p>Texto</p>').includes('Texto'));
});
