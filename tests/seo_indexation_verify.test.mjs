import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';

import {
  CHILD_SITEMAPS,
  EXPECTED,
  HOST,
  auditIndexation,
  parseLocs,
  routeFileForUrl,
} from '../seo_indexation_verify.mjs';

function write(file, content = '<!doctype html><title>fixture</title>') {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, content, 'utf8');
}

function makeFixture() {
  const base = fs.mkdtempSync(path.join(os.tmpdir(), 'seo-indexation-'));
  for (const [repo, spec] of Object.entries(EXPECTED)) {
    const repoDir = path.join(base, repo);
    fs.mkdirSync(repoDir, { recursive: true });
    const entries = spec.urls.map((url) => `  <url><loc>${url}</loc></url>`).join('\n');
    write(path.join(repoDir, spec.sitemap), `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${entries}\n</urlset>\n`);
    for (const url of spec.urls) {
      write(path.join(repoDir, routeFileForUrl(repo, url)));
    }
  }

  const root = path.join(base, 'crebeucayali.github.io');
  write(path.join(root, 'robots.txt'), `User-agent: *\nAllow: /\n\nSitemap: ${HOST}sitemap-v2.xml\n`);
  const children = CHILD_SITEMAPS.map((url) => `  <sitemap><loc>${url}</loc></sitemap>`).join('\n');
  write(path.join(root, 'sitemap-v2.xml'), `<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${children}\n</sitemapindex>\n`);
  return base;
}

test('extrae locs desde sitemap XML', () => {
  assert.deepEqual(parseLocs('<urlset><url><loc>https://a/</loc></url><url><loc>https://b/</loc></url></urlset>'), ['https://a/', 'https://b/']);
});

test('resuelve URLs oficiales al archivo fuente esperado', () => {
  assert.equal(routeFileForUrl('crebeucayali.github.io', `${HOST}`), 'index.html');
  assert.equal(routeFileForUrl('crebeucayali.github.io', `${HOST}buscar/`), 'buscar/index.html');
  assert.equal(routeFileForUrl('DUA-3.0', `${HOST}DUA-3.0/recursos.html`), 'recursos.html');
  assert.equal(routeFileForUrl('noti-inclusivos', `${HOST}noti-inclusivos/articulos/`), 'articulos/index.html');
});

test('valida la arquitectura completa con ocho sitemaps y 56 URLs oficiales', () => {
  const base = makeFixture();
  try {
    const report = auditIndexation(base);
    assert.equal(report.totals.repositories, 8);
    assert.equal(report.totals.child_sitemaps, 8);
    assert.equal(report.totals.indexed_urls, 56);
    assert.equal(report.totals.duplicate_urls, 0);
    assert.equal(report.totals.missing_route_files, 0);
    assert.equal(report.root_discovery.robots_declares_central_index, true);
  } finally {
    fs.rmSync(base, { recursive: true, force: true });
  }
});

test('rechaza una URL del sitemap cuyo archivo fuente no existe', () => {
  const base = makeFixture();
  try {
    fs.rmSync(path.join(base, 'DUA-3.0', 'recursos.html'));
    assert.throws(() => auditIndexation(base), /Rutas del sitemap sin archivo fuente/);
  } finally {
    fs.rmSync(base, { recursive: true, force: true });
  }
});
