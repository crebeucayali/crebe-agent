import test from 'node:test';
import assert from 'node:assert/strict';
import {
  extractHrefs,
  buildOfficialLookup,
  classifyHref,
  graphMetrics,
} from '../seo_internal_links_verify.mjs';
import { HOST } from '../seo_indexation_verify.mjs';

test('extrae href con comillas dobles, simples y sin comillas', () => {
  const html = '<a href="uno.html">Uno</a><a href=\'dos.html\'>Dos</a><a href=tres.html>Tres</a>';
  assert.deepEqual(extractHrefs(html), ['uno.html', 'dos.html', 'tres.html']);
});

test('normaliza enlaces relativos hacia una URL oficial', () => {
  const lookup = buildOfficialLookup();
  const source = `${HOST}accesos-complementarios/paginas/nosotros.html`;
  const result = classifyHref(source, '../mapa-web.html#contenido', lookup);
  assert.equal(result.kind, 'official_internal');
  assert.equal(result.url, `${HOST}accesos-complementarios/mapa-web.html`);
});

test('distingue enlaces externos y rutas internas no oficiales', () => {
  const lookup = buildOfficialLookup();
  const source = `${HOST}accesos-complementarios/`;
  assert.equal(classifyHref(source, 'https://example.org/recurso', lookup).kind, 'external');
  assert.equal(classifyHref(source, './admin/', lookup).kind, 'other_internal');
});

test('calcula huérfanas y alcanzabilidad desde la raíz', () => {
  const urls = [HOST, `${HOST}a/`, `${HOST}b/`, `${HOST}c/`];
  const edges = [
    [HOST, `${HOST}a/`],
    [`${HOST}a/`, `${HOST}b/`],
    [`${HOST}c/`, `${HOST}c/`],
  ];
  const metrics = graphMetrics(urls, edges, HOST);
  assert.deepEqual(metrics.orphanUrls, [`${HOST}c/`]);
  assert.deepEqual(metrics.unreachableUrls, [`${HOST}c/`]);
  assert.deepEqual(metrics.withoutOutgoing, [`${HOST}b/`]);
});
