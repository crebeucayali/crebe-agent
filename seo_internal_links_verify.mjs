import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { EXPECTED, HOST, routeFileForUrl } from './seo_indexation_verify.mjs';

function decodeHref(value = '') {
  return value
    .replace(/&amp;/gi, '&')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/gi, "'")
    .trim();
}

export function extractHrefs(html = '') {
  const hrefs = [];
  const re = /<a\b[^>]*\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))[^>]*>/gi;
  for (const match of html.matchAll(re)) {
    hrefs.push(decodeHref(match[1] ?? match[2] ?? match[3] ?? ''));
  }
  return hrefs;
}

export function canonicalUrlKey(value) {
  const url = new URL(value);
  url.hash = '';
  url.search = '';
  if (/\/index\.html$/i.test(url.pathname)) {
    url.pathname = url.pathname.replace(/index\.html$/i, '');
  }
  return url.href;
}

export function buildOfficialLookup(expected = EXPECTED) {
  const lookup = new Map();
  for (const spec of Object.values(expected)) {
    for (const officialUrl of spec.urls) {
      const canonical = canonicalUrlKey(officialUrl);
      lookup.set(canonical, officialUrl);
      if (officialUrl.endsWith('/')) lookup.set(`${officialUrl}index.html`, officialUrl);
    }
  }
  return lookup;
}

export function classifyHref(sourceUrl, href, lookup = buildOfficialLookup()) {
  const raw = (href ?? '').trim();
  if (!raw || raw.startsWith('#')) return { kind: 'fragment_or_empty' };
  if (/^(?:mailto:|tel:|javascript:|data:|blob:)/i.test(raw)) return { kind: 'non_http' };

  let resolved;
  try {
    resolved = new URL(raw, sourceUrl);
  } catch {
    return { kind: 'invalid_url', href: raw };
  }

  if (!/^https?:$/.test(resolved.protocol)) return { kind: 'non_http' };
  const officialHost = new URL(HOST).host;
  if (resolved.host !== officialHost) return { kind: 'external', url: resolved.href };

  const nonHttps = resolved.protocol !== 'https:';
  resolved.protocol = 'https:';
  resolved.hash = '';
  resolved.search = '';
  const key = canonicalUrlKey(resolved.href);
  const official = lookup.get(key) ?? lookup.get(resolved.href);
  if (official) return { kind: 'official_internal', url: official, non_https: nonHttps };
  return { kind: 'other_internal', url: resolved.href, non_https: nonHttps };
}

export function graphMetrics(officialUrls, edges, rootUrl = HOST) {
  const incoming = new Map(officialUrls.map((url) => [url, new Set()]));
  const outgoing = new Map(officialUrls.map((url) => [url, new Set()]));

  for (const [source, target] of edges) {
    if (!incoming.has(target) || !outgoing.has(source)) continue;
    outgoing.get(source).add(target);
    if (source !== target) incoming.get(target).add(source);
  }

  const orphanUrls = officialUrls.filter((url) => url !== rootUrl && incoming.get(url).size === 0);
  const withoutOutgoing = officialUrls.filter((url) => outgoing.get(url).size === 0);

  const visited = new Set();
  const queue = [rootUrl];
  while (queue.length) {
    const current = queue.shift();
    if (visited.has(current) || !outgoing.has(current)) continue;
    visited.add(current);
    for (const target of outgoing.get(current)) {
      if (!visited.has(target)) queue.push(target);
    }
  }
  const unreachableUrls = officialUrls.filter((url) => !visited.has(url));

  return {
    incoming,
    outgoing,
    orphanUrls,
    withoutOutgoing,
    unreachableUrls,
    reachableUrls: [...visited],
  };
}

export function auditInternalLinks(baseDir) {
  const lookup = buildOfficialLookup();
  const entries = [];
  for (const [repo, spec] of Object.entries(EXPECTED)) {
    for (const url of spec.urls) {
      entries.push({ repo, url, file: routeFileForUrl(repo, url) });
    }
  }

  const officialUrls = entries.map((entry) => entry.url);
  const edges = [];
  const pages = [];
  let invalidHrefCount = 0;
  let otherInternalCount = 0;
  let externalCount = 0;
  let nonHttpsInternalCount = 0;
  let missingFiles = 0;

  for (const entry of entries) {
    const source = path.join(baseDir, entry.repo, entry.file);
    if (!fs.existsSync(source)) {
      missingFiles += 1;
      pages.push({ ...entry, status: 'FAIL', errors: ['missing_route_file'], official_outgoing: [], other_internal: [] });
      continue;
    }

    const hrefs = extractHrefs(fs.readFileSync(source, 'utf8'));
    const officialOutgoing = new Set();
    const otherInternal = new Set();
    const errors = [];

    for (const href of hrefs) {
      const classified = classifyHref(entry.url, href, lookup);
      if (classified.kind === 'official_internal') {
        officialOutgoing.add(classified.url);
        edges.push([entry.url, classified.url]);
        if (classified.non_https) nonHttpsInternalCount += 1;
      } else if (classified.kind === 'other_internal') {
        otherInternal.add(classified.url);
        otherInternalCount += 1;
        if (classified.non_https) nonHttpsInternalCount += 1;
      } else if (classified.kind === 'external') {
        externalCount += 1;
      } else if (classified.kind === 'invalid_url') {
        invalidHrefCount += 1;
        errors.push('invalid_href');
      }
    }

    pages.push({
      ...entry,
      href_count: hrefs.length,
      official_outgoing: [...officialOutgoing].sort(),
      official_outgoing_count: officialOutgoing.size,
      other_internal: [...otherInternal].sort(),
      other_internal_count: otherInternal.size,
      status: errors.length ? 'WARN' : 'PASS',
      errors: [...new Set(errors)],
    });
  }

  const metrics = graphMetrics(officialUrls, edges, HOST);
  const pageByUrl = new Map(pages.map((page) => [page.url, page]));
  for (const url of officialUrls) {
    const page = pageByUrl.get(url);
    if (!page) continue;
    page.official_incoming_count = metrics.incoming.get(url)?.size ?? 0;
    page.official_incoming = [...(metrics.incoming.get(url) ?? [])].sort();
    page.reachable_from_root = metrics.reachableUrls.includes(url);
  }

  return {
    schema_version: 1,
    fase: 9,
    etapa: 6,
    nombre: 'Enlazado interno',
    modo: 'READ_ONLY_INTERNAL_LINK_VERIFY',
    totals: {
      repositories: Object.keys(EXPECTED).length,
      official_urls: officialUrls.length,
      official_edges: new Set(edges.map(([source, target]) => `${source} -> ${target}`)).size,
      missing_route_files: missingFiles,
      orphan_pages: metrics.orphanUrls.length,
      unreachable_from_root: metrics.unreachableUrls.length,
      pages_without_official_outgoing: metrics.withoutOutgoing.length,
      other_internal_links: otherInternalCount,
      invalid_hrefs: invalidHrefCount,
      non_https_internal_links: nonHttpsInternalCount,
      external_links: externalCount,
    },
    orphan_urls: metrics.orphanUrls,
    unreachable_urls: metrics.unreachableUrls,
    pages_without_official_outgoing: metrics.withoutOutgoing,
    pages,
    guardrails: {
      read_only: true,
      repositorios_eva_modificados_por_verificador: false,
      contenido_reescrito_por_verificador: false,
      canonical_modificado_por_verificador: false,
      metadata_modificada_por_verificador: false,
      supabase_modificado: false,
      panel_administrativo_modificado: false,
      archivos_accesibilidad_modificados: false,
      etapa_7_iniciada: false,
    },
  };
}

function main() {
  const [, , baseDir = '_eva', output = 'reports/fase-9-etapa-6-enlazado-interno.generated.json'] = process.argv;
  const report = auditInternalLinks(baseDir);
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  console.log(JSON.stringify({ totals: report.totals, orphan_urls: report.orphan_urls, unreachable_urls: report.unreachable_urls, pages_without_official_outgoing: report.pages_without_official_outgoing }, null, 2));
}

const current = fileURLToPath(import.meta.url);
if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(current)) main();
