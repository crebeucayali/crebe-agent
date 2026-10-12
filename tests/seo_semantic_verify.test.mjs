import test from 'node:test';
import assert from 'node:assert/strict';
import { inspectEntry, sha256Source, ROOT_URL, ORGANIZATION_ID, WEBSITE_ID, ORGANIZATION_NAME, WEBSITE_NAME } from '../seo_semantic_verify.mjs';

function moduleHtml({ canonical = `${ROOT_URL}capacitaciones/`, title = 'Capacitaciones', description = 'Descripción', orgName = ORGANIZATION_NAME, pageName = title, cspHash = true } = {}) {
  const data = {
    '@context': 'https://schema.org',
    '@graph': [
      { '@type': 'EducationalOrganization', '@id': ORGANIZATION_ID, name: orgName, alternateName: 'CREBE Ucayali', url: ROOT_URL, logo: `${ROOT_URL}accesos-complementarios/logo-crebe.webp` },
      { '@type': 'WebSite', '@id': WEBSITE_ID, name: WEBSITE_NAME, url: ROOT_URL, publisher: { '@id': ORGANIZATION_ID } },
      { '@type': 'WebPage', '@id': `${canonical}#webpage`, url: canonical, name: pageName, description, isPartOf: { '@id': WEBSITE_ID }, publisher: { '@id': ORGANIZATION_ID }, inLanguage: 'es-PE' },
    ],
  };
  const body = `\n${JSON.stringify(data, null, 2)}\n`;
  const source = sha256Source(body);
  const csp = `default-src 'self'; script-src 'self'${cspHash ? ` '${source}'` : ''}; style-src 'self'`;
  return `<html><head><meta http-equiv="Content-Security-Policy" content="${csp}"><meta name="description" content="${description}"><title>${title}</title><script type="application/ld+json">${body}</script><link rel="canonical" href="${canonical}"></head></html>`;
}

test('inspectEntry aprueba identidad, metadata y hash CSP coherentes', () => {
  const canonical = `${ROOT_URL}capacitaciones/`;
  const result = inspectEntry('capacitaciones', moduleHtml({ canonical }), canonical);
  assert.equal(result.status, 'PASS');
  assert.equal(result.identity_mismatch, 0);
  assert.equal(result.page_metadata_mismatch, 0);
  assert.equal(result.csp_hash_mismatch, 0);
});

test('inspectEntry detecta identidad institucional inconsistente', () => {
  const canonical = `${ROOT_URL}capacitaciones/`;
  const result = inspectEntry('capacitaciones', moduleHtml({ canonical, orgName: 'Otra entidad' }), canonical);
  assert.equal(result.status, 'FAIL');
  assert.equal(result.identity_mismatch, 1);
  assert.ok(result.errors.includes('identity_mismatch'));
});

test('inspectEntry detecta metadata de WebPage distinta del title real', () => {
  const canonical = `${ROOT_URL}capacitaciones/`;
  const result = inspectEntry('capacitaciones', moduleHtml({ canonical, pageName: 'Nombre distinto' }), canonical);
  assert.equal(result.page_metadata_mismatch, 1);
  assert.ok(result.errors.includes('page_metadata_mismatch'));
});

test('inspectEntry detecta JSON-LD no autorizado por CSP', () => {
  const canonical = `${ROOT_URL}capacitaciones/`;
  const result = inspectEntry('capacitaciones', moduleHtml({ canonical, cspHash: false }), canonical);
  assert.equal(result.csp_hash_mismatch, 1);
  assert.ok(result.errors.includes('csp_hash_mismatch'));
});
