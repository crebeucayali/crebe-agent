import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { EXPECTED, HOST, routeFileForUrl } from './seo_indexation_verify.mjs';

function attr(tag, name) {
  const re = new RegExp(`\\b${name}\\s*=\\s*(["'])(.*?)\\1`, 'i');
  return tag.match(re)?.[2]?.trim() ?? '';
}

export function metadataForHtml(html) {
  const title = html.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i)?.[1]?.replace(/\s+/g, ' ').trim() ?? '';
  const metaTags = [...html.matchAll(/<meta\b[^>]*>/gi)].map((m) => m[0]);
  const linkTags = [...html.matchAll(/<link\b[^>]*>/gi)].map((m) => m[0]);
  const descriptionTag = metaTags.find((tag) => attr(tag, 'name').toLowerCase() === 'description');
  const robotsTag = metaTags.find((tag) => attr(tag, 'name').toLowerCase() === 'robots');
  const canonicals = linkTags
    .filter((tag) => attr(tag, 'rel').toLowerCase().split(/\s+/).includes('canonical'))
    .map((tag) => attr(tag, 'href'))
    .filter(Boolean);
  return {
    title,
    description: descriptionTag ? attr(descriptionTag, 'content') : '',
    robots: robotsTag ? attr(robotsTag, 'content') : '',
    canonicals,
  };
}

export function auditMetadata(baseDir) {
  const findings = {
    missing_title: [],
    missing_description: [],
    missing_canonical: [],
    duplicate_canonical: [],
    canonical_mismatch: [],
    invalid_canonical_host: [],
  };
  const repositories = [];
  const noindexUrls = [];
  let officialUrls = 0;
  let indexableUrls = 0;

  for (const [repo, spec] of Object.entries(EXPECTED)) {
    const repoDir = path.join(baseDir, repo);
    let repoOfficial = 0;
    let repoIndexable = 0;

    for (const url of spec.urls) {
      officialUrls += 1;
      repoOfficial += 1;
      const routeFile = routeFileForUrl(repo, url);
      const filePath = path.join(repoDir, routeFile);
      if (!fs.existsSync(filePath)) throw new Error(`Falta archivo fuente para ${url}: ${repo}/${routeFile}`);
      const html = fs.readFileSync(filePath, 'utf8');
      const metadata = metadataForHtml(html);
      const noindex = /(?:^|[\s,])noindex(?:$|[\s,])/i.test(metadata.robots);
      if (noindex) {
        noindexUrls.push({ repo, url, route_file: routeFile });
        continue;
      }

      indexableUrls += 1;
      repoIndexable += 1;
      const item = { repo, url, route_file: routeFile };
      if (!metadata.title) findings.missing_title.push(item);
      if (!metadata.description) findings.missing_description.push(item);
      if (metadata.canonicals.length === 0) findings.missing_canonical.push(item);
      if (metadata.canonicals.length > 1) findings.duplicate_canonical.push({ ...item, canonicals: metadata.canonicals });
      if (metadata.canonicals.length === 1) {
        const canonical = metadata.canonicals[0];
        if (!canonical.startsWith(HOST)) findings.invalid_canonical_host.push({ ...item, canonical });
        if (canonical !== url) findings.canonical_mismatch.push({ ...item, canonical });
      }
    }

    repositories.push({ repo, official_urls: repoOfficial, indexable_urls: repoIndexable });
  }

  return {
    schema_version: 1,
    fase: 9,
    etapa: 3,
    nombre: 'Canonical y metadata',
    modo: 'READ_ONLY_METADATA_VERIFY',
    generated_at: new Date().toISOString(),
    totals: {
      repositories: Object.keys(EXPECTED).length,
      official_urls: officialUrls,
      indexable_urls: indexableUrls,
      noindex_urls: noindexUrls.length,
      missing_title: findings.missing_title.length,
      missing_description: findings.missing_description.length,
      missing_canonical: findings.missing_canonical.length,
      duplicate_canonical: findings.duplicate_canonical.length,
      canonical_mismatch: findings.canonical_mismatch.length,
      invalid_canonical_host: findings.invalid_canonical_host.length,
    },
    repositories,
    noindex_urls: noindexUrls,
    findings,
    guardrails: {
      read_only: true,
      repositorios_eva_modificados_por_verificador: false,
      supabase_modificado: false,
      panel_administrativo_modificado: false,
      etapa_4_iniciada: false,
    },
  };
}

function main() {
  const [baseDir = '_eva', output = 'reports/fase-9-etapa-3-canonical-metadata.generated.json'] = process.argv.slice(2);
  const report = auditMetadata(baseDir);
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  console.log(JSON.stringify({ totals: report.totals, guardrails: report.guardrails }, null, 2));
  const t = report.totals;
  if (t.missing_title || t.missing_description || t.missing_canonical || t.duplicate_canonical || t.canonical_mismatch || t.invalid_canonical_host) {
    process.exitCode = 1;
  }
}

const current = fileURLToPath(import.meta.url);
if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(current)) main();
