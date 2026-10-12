import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { metadataForHtml } from './seo_metadata_verify.mjs';

export const ROOT_URL = 'https://crebeucayali.github.io/';
export const ORGANIZATION_ID = `${ROOT_URL}#organization`;
export const WEBSITE_ID = `${ROOT_URL}#website`;
export const ORGANIZATION_NAME = 'CREBE Señor de los Milagros - Ucayali';
export const WEBSITE_NAME = 'CREBE Señor de los Milagros Región Ucayali';

export const ENTRY_PAGES = {
  'crebeucayali.github.io': ROOT_URL,
  'accesos-complementarios': `${ROOT_URL}accesos-complementarios/`,
  capacitaciones: `${ROOT_URL}capacitaciones/`,
  'banco-digital-accesible': `${ROOT_URL}banco-digital-accesible/`,
  'materiales-educativos-accesibles': `${ROOT_URL}materiales-educativos-accesibles/`,
  'noti-inclusivos': `${ROOT_URL}noti-inclusivos/`,
  'repositorio-accesible': `${ROOT_URL}repositorio-accesible/`,
  'DUA-3.0': `${ROOT_URL}DUA-3.0/`,
};

export function jsonLdBodies(html) {
  return [...html.matchAll(/<script\b[^>]*\btype=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)].map((m) => m[1]);
}

export function cspContent(html) {
  for (const tag of html.match(/<meta\b[^>]*>/gi) || []) {
    if (!/http-equiv\s*=\s*["']Content-Security-Policy["']/i.test(tag)) continue;
    const m = tag.match(/content\s*=\s*(["'])([\s\S]*?)\1/i);
    if (m) return m[2];
  }
  return '';
}

export function sha256Source(body) {
  return `sha256-${crypto.createHash('sha256').update(body, 'utf8').digest('base64')}`;
}

function flattenEntities(value) {
  if (!value || typeof value !== 'object') return [];
  if (Array.isArray(value)) return value.flatMap(flattenEntities);
  if (Array.isArray(value['@graph'])) return value['@graph'].flatMap(flattenEntities);
  return [value];
}

function refId(value) {
  return value && typeof value === 'object' ? value['@id'] : null;
}

export function inspectEntry(repo, html, canonical) {
  const meta = metadataForHtml(html);
  const bodies = jsonLdBodies(html);
  const csp = cspContent(html);
  const errors = [];
  const parsed = [];
  let invalidJsonLd = 0;
  let cspHashMismatch = 0;
  for (const body of bodies) {
    try { parsed.push(JSON.parse(body)); }
    catch { invalidJsonLd += 1; }
    const source = sha256Source(body);
    if (!csp.includes(`'${source}'`)) cspHashMismatch += 1;
  }
  if (bodies.length === 0) errors.push('missing_jsonld');
  if (invalidJsonLd) errors.push('invalid_jsonld');
  if (cspHashMismatch) errors.push('csp_hash_mismatch');

  const entities = parsed.flatMap(flattenEntities);
  let identityMismatch = 0;
  let pageMetadataMismatch = 0;

  if (repo === 'crebeucayali.github.io') {
    const site = entities.find((e) => e['@type'] === 'WebSite');
    if (!site || site.name !== WEBSITE_NAME || site.url !== ROOT_URL) identityMismatch += 1;
  } else {
    if (bodies.length !== 1) errors.push('unexpected_jsonld_block_count');
    const org = entities.find((e) => e['@type'] === 'EducationalOrganization');
    const site = entities.find((e) => e['@type'] === 'WebSite');
    const page = entities.find((e) => e['@type'] === 'WebPage');

    if (!org || org['@id'] !== ORGANIZATION_ID || org.name !== ORGANIZATION_NAME || org.url !== ROOT_URL) identityMismatch += 1;
    if (!site || site['@id'] !== WEBSITE_ID || site.name !== WEBSITE_NAME || site.url !== ROOT_URL || refId(site.publisher) !== ORGANIZATION_ID) identityMismatch += 1;
    if (!page || page['@id'] !== `${canonical}#webpage` || page.url !== canonical || refId(page.isPartOf) !== WEBSITE_ID || refId(page.publisher) !== ORGANIZATION_ID || page.inLanguage !== 'es-PE') identityMismatch += 1;
    if (!page || page.name !== meta.title || page.description !== meta.description || meta.canonicals.length !== 1 || meta.canonicals[0] !== canonical) pageMetadataMismatch += 1;
  }

  if (identityMismatch) errors.push('identity_mismatch');
  if (pageMetadataMismatch) errors.push('page_metadata_mismatch');

  return {
    repo,
    canonical,
    jsonld_blocks: bodies.length,
    invalid_jsonld: invalidJsonLd,
    identity_mismatch: identityMismatch,
    page_metadata_mismatch: pageMetadataMismatch,
    csp_hash_mismatch: cspHashMismatch,
    status: errors.length ? 'FAIL' : 'PASS',
    errors,
  };
}

export function auditSemantic(baseDir) {
  const entries = [];
  for (const [repo, canonical] of Object.entries(ENTRY_PAGES)) {
    const file = path.join(baseDir, repo, 'index.html');
    if (!fs.existsSync(file)) {
      entries.push({ repo, canonical, status: 'FAIL', errors: ['missing_entry_file'], jsonld_blocks: 0, invalid_jsonld: 0, identity_mismatch: 0, page_metadata_mismatch: 0, csp_hash_mismatch: 0 });
      continue;
    }
    entries.push(inspectEntry(repo, fs.readFileSync(file, 'utf8'), canonical));
  }
  const sum = (key) => entries.reduce((n, item) => n + (item[key] || 0), 0);
  const failing = entries.filter((item) => item.status !== 'PASS').length;
  return {
    schema_version: 1,
    fase: 9,
    etapa: 4,
    nombre: 'Identidad semantica y datos estructurados',
    modo: 'READ_ONLY_SEMANTIC_VERIFY',
    totals: {
      repositories: 8,
      entry_pages: 8,
      root_preexisting_structured_data: 1,
      module_pages_enriched: 7,
      pages_with_structured_data: entries.filter((item) => item.jsonld_blocks > 0).length,
      invalid_jsonld: sum('invalid_jsonld'),
      identity_mismatch: sum('identity_mismatch'),
      page_metadata_mismatch: sum('page_metadata_mismatch'),
      csp_hash_mismatch: sum('csp_hash_mismatch'),
      failing_pages: failing,
    },
    entries,
    guardrails: {
      read_only: true,
      repositorios_eva_modificados_por_verificador: false,
      contenido_visible_modificado_por_verificador: false,
      css_modificado_por_verificador: false,
      javascript_funcional_modificado_por_verificador: false,
      supabase_modificado: false,
      panel_administrativo_modificado: false,
      accesibilidad_modificada: false,
      etapa_5_iniciada: false,
    },
  };
}

function main() {
  const [, , baseDir = '_eva', output = 'reports/fase-9-etapa-4-identidad-semantica.generated.json'] = process.argv;
  const report = auditSemantic(baseDir);
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  console.log(JSON.stringify(report.totals));
  if (report.totals.failing_pages > 0) process.exitCode = 1;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) main();
