import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { analyzeHtml, auditWorkspace, EXPECTED_REPOS, parseSitemapUrls } from '../seo_audit.mjs';

test('extrae señales SEO principales de una página HTML', () => {
  const html = `<!doctype html><html lang="es"><head>
    <title>Lengua de Señas Peruana | CREBE Ucayali</title>
    <meta name="description" content="Recursos de LSP para inclusión educativa">
    <link rel="canonical" href="https://crebeucayali.github.io/banco-digital-accesible/lsp/">
    <script type="application/ld+json">{"@context":"https://schema.org","@type":"WebPage"}</script>
  </head><body><h1>Lengua de Señas Peruana</h1><p>Accesibilidad e inclusión educativa.</p></body></html>`;
  const page = analyzeHtml(html, 'lsp/index.html');
  assert.equal(page.title, 'Lengua de Señas Peruana | CREBE Ucayali');
  assert.equal(page.description, 'Recursos de LSP para inclusión educativa');
  assert.equal(page.canonical, 'https://crebeucayali.github.io/banco-digital-accesible/lsp/');
  assert.equal(page.noindex, false);
  assert.equal(page.h1_count, 1);
  assert.deepEqual(page.json_ld_types, ['WebPage']);
  assert.equal(page.terms.lsp, true);
  assert.equal(page.terms.inclusion_educativa, true);
});

test('reconoce noindex y ausencia de canonical', () => {
  const page = analyzeHtml('<html><head><meta name="robots" content="noindex,follow"><title>Auxiliar</title></head><body><h1>Auxiliar</h1></body></html>', 'aux.html');
  assert.equal(page.noindex, true);
  assert.equal(page.canonical, null);
});

test('extrae URLs de sitemap', () => {
  const urls = parseSitemapUrls('<?xml version="1.0"?><urlset><url><loc>https://crebeucayali.github.io/</loc></url><url><loc>https://crebeucayali.github.io/capacitaciones/</loc></url></urlset>');
  assert.deepEqual(urls, ['https://crebeucayali.github.io/', 'https://crebeucayali.github.io/capacitaciones/']);
});

test('audita exactamente los ocho repositorios sin escribir sobre ellos', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'crebe-seo-'));
  try {
    for (const repo of EXPECTED_REPOS) {
      const repoDir = path.join(root, repo);
      fs.mkdirSync(repoDir, { recursive: true });
      fs.writeFileSync(path.join(repoDir, 'index.html'), `<!doctype html><html><head><title>${repo}</title><meta name="description" content="Inclusión y accesibilidad"><link rel="canonical" href="https://crebeucayali.github.io/${repo === 'crebeucayali.github.io' ? '' : `${repo}/`}"></head><body><h1>${repo}</h1></body></html>`);
      if (repo === 'crebeucayali.github.io') {
        fs.writeFileSync(path.join(repoDir, 'robots.txt'), 'User-agent: *\nAllow: /\nSitemap: https://crebeucayali.github.io/sitemap-v2.xml\n');
        fs.writeFileSync(path.join(repoDir, 'sitemap-v2.xml'), '<urlset><url><loc>https://crebeucayali.github.io/</loc></url></urlset>');
      } else {
        fs.writeFileSync(path.join(repoDir, 'sitemap.xml'), `<urlset><url><loc>https://crebeucayali.github.io/${repo}/</loc></url></urlset>`);
      }
    }
    const report = auditWorkspace(root);
    assert.equal(report.totals.repositories, 8);
    assert.equal(report.guardrails.read_only, true);
    assert.equal(report.guardrails.repositorios_eva_modificados, false);
    assert.equal(report.root_discovery.root_sitemap_urls, 1);
    assert.equal(report.findings.some((f) => f.code === 'ROOT_SITEMAP_LIMITED'), true);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
