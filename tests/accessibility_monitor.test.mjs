import test from 'node:test';
import assert from 'node:assert/strict';
import { OVERFLOW_TARGETS, evaluateSummary, isAuxiliary, publicUrl } from '../accessibility_monitor.mjs';

test('construye URLs públicas para raíz y subrepositorios', () => {
  assert.equal(publicUrl('crebeucayali.github.io', 'index.html'), 'https://crebeucayali.github.io/');
  assert.equal(publicUrl('capacitaciones', 'index.html'), 'https://crebeucayali.github.io/capacitaciones/');
  assert.equal(publicUrl('DUA-3.0', 'recursos.html'), 'https://crebeucayali.github.io/DUA-3.0/recursos.html');
});

test('excluye únicamente páginas auxiliares conocidas', () => {
  assert.equal(isAuxiliary('google09722cd21d5d281a.html'), true);
  assert.equal(isAuxiliary('docs/referencias/ejemplo.html'), true);
  assert.equal(isAuxiliary('paginas/contacto.html'), false);
});

test('resultado limpio no genera alertas', () => {
  const overflowDetail = [...OVERFLOW_TARGETS].map(path => ({ path, horizontalOverflow: false }));
  const result = evaluateSummary({ loadFailures: [], contrastNodes: 0, overflowDetail });
  assert.equal(result.estado, 'SIN_REGRESIONES_AUTOMATIZADAS');
  assert.deepEqual(result.alertas, []);
  assert.equal(result.overflowFailures.length, 0);
});

test('detecta regresiones automatizadas', () => {
  const overflowDetail = [{ path: 'x', horizontalOverflow: true }];
  const result = evaluateSummary({ loadFailures: [{ path: 'fallo.html' }], contrastNodes: 2, overflowDetail });
  assert.equal(result.estado, 'ALERTA');
  assert.equal(result.alertas.length, 4);
  assert.equal(result.overflowFailures.length, 1);
});
