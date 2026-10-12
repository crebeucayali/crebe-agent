import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { metadataForHtml, auditMetadata } from '../seo_metadata_verify.mjs';
import { EXPECTED, routeFileForUrl } from '../seo_indexation_verify.mjs';

test('metadataForHtml reconoce title, description, robots y canonical', () => {
  const html = '<html><head><title>Ejemplo</title><meta name="description" content="Descripción"><meta name="robots" content="index,follow"><link rel="canonical" href="https://crebeucayali.github.io/ejemplo/"></head></html>';
  assert.deepEqual(metadataForHtml(html), {
    title: 'Ejemplo',
    description: 'Descripción',
    robots: 'index,follow',
    canonicals: ['https://crebeucayali.github.io/ejemplo/'],
  });
});

test('metadataForHtml admite atributos en distinto orden', () => {
  const html = '<head><title>Ruta</title><meta content="Descripción" name="description"><link href="https://crebeucayali.github.io/" rel="canonical"></head>';
  const meta = metadataForHtml(html);
  assert.equal(meta.description, 'Descripción');
  assert.deepEqual(meta.canonicals, ['https://crebeucayali.github.io/']);
});

test('auditMetadata omite requisitos de indexación en páginas noindex', () => {
  const base = fs.mkdtempSync(path.join(os.tmpdir(), 'seo-meta-'));
  for (const [repo, spec] of Object.entries(EXPECTED)) {
    const repoDir = path.join(base, repo);
    fs.mkdirSync(repoDir, { recursive: true });
    for (const url of spec.urls) {
      const file = path.join(repoDir, routeFileForUrl(repo, url));
      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.writeFileSync(file, `<head><title>${repo}</title><meta name="description" content="OK"><link rel="canonical" href="${url}"></head>`, 'utf8');
    }
  }
  const noindexUrl = EXPECTED['accesos-complementarios'].urls.find((url) => url.endsWith('/mapa-web.html'));
  const noindexFile = path.join(base, 'accesos-complementarios', routeFileForUrl('accesos-complementarios', noindexUrl));
  fs.writeFileSync(noindexFile, '<head><title>Mapa</title><meta name="robots" content="noindex,follow"></head>', 'utf8');
  const report = auditMetadata(base);
  assert.equal(report.totals.official_urls, 56);
  assert.equal(report.totals.noindex_urls, 1);
  assert.equal(report.totals.missing_title, 0);
  assert.equal(report.totals.missing_description, 0);
  assert.equal(report.totals.missing_canonical, 0);
});

test('auditMetadata detecta canonical distinto de la URL oficial', () => {
  const base = fs.mkdtempSync(path.join(os.tmpdir(), 'seo-meta-'));
  for (const [repo, spec] of Object.entries(EXPECTED)) {
    const repoDir = path.join(base, repo);
    fs.mkdirSync(repoDir, { recursive: true });
    for (const url of spec.urls) {
      const file = path.join(repoDir, routeFileForUrl(repo, url));
      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.writeFileSync(file, `<head><title>${repo}</title><meta name="description" content="OK"><link rel="canonical" href="${url}"></head>`, 'utf8');
    }
  }
  const first = EXPECTED['crebeucayali.github.io'].urls[0];
  const file = path.join(base, 'crebeucayali.github.io', routeFileForUrl('crebeucayali.github.io', first));
  fs.writeFileSync(file, '<head><title>Inicio</title><meta name="description" content="OK"><link rel="canonical" href="https://crebeucayali.github.io/otra/"></head>', 'utf8');
  const report = auditMetadata(base);
  assert.equal(report.totals.canonical_mismatch, 1);
});
