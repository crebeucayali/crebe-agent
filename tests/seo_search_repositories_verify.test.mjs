import test from 'node:test';
import assert from 'node:assert/strict';
import { inspectRepository, inspectRobots, inspectSitemap } from '../seo_search_repositories_verify.mjs';

test('inspectRepository valida exposición pública y homepage', () => {
  const result = inspectRepository({ private: false, archived: false, has_pages: true, homepage: 'https://crebeucayali.github.io/capacitaciones/', description: 'x', topics: ['eva'] }, 'https://crebeucayali.github.io/capacitaciones/');
  assert.equal(result.public, true);
  assert.equal(result.archived, false);
  assert.equal(result.pages_enabled, true);
  assert.equal(result.homepage_matches_expected, true);
  assert.equal(result.description_present, true);
  assert.equal(result.topics_count, 1);
});

test('inspectRobots exige apertura raíz y sitemap institucional', () => {
  const result = inspectRobots('User-agent: *\nAllow: /\nSitemap: https://crebeucayali.github.io/sitemap-v2.xml\n');
  assert.deepEqual(result, { allows_root: true, sitemap_declared: true });
});

test('inspectSitemap detecta cobertura completa de 8 entradas', () => {
  const urls = [
    'https://crebeucayali.github.io/sitemap-main.xml',
    'https://crebeucayali.github.io/accesos-complementarios/sitemap.xml',
    'https://crebeucayali.github.io/capacitaciones/sitemap.xml',
    'https://crebeucayali.github.io/banco-digital-accesible/sitemap.xml',
    'https://crebeucayali.github.io/materiales-educativos-accesibles/sitemap.xml',
    'https://crebeucayali.github.io/noti-inclusivos/sitemap.xml',
    'https://crebeucayali.github.io/repositorio-accesible/sitemap.xml',
    'https://crebeucayali.github.io/DUA-3.0/sitemap.xml',
  ];
  const xml = urls.map((u) => `<loc>${u}</loc>`).join('\n');
  const result = inspectSitemap(xml);
  assert.equal(result.expected_entries, 8);
  assert.deepEqual(result.missing_entries, []);
});
