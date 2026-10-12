import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

export const EXPECTED_REPOS = [
  'crebeucayali.github.io',
  'accesos-complementarios',
  'capacitaciones',
  'banco-digital-accesible',
  'materiales-educativos-accesibles',
  'noti-inclusivos',
  'repositorio-accesible',
  'DUA-3.0',
];

const TERM_PATTERNS = {
  inclusion_educativa: /educaci[oó]n inclusiv|inclusi[oó]n educativa/i,
  inclusion: /inclusi[oó]n|inclusiv/i,
  accesibilidad: /accesibilidad|accesible/i,
  discapacidad: /discapacidad/i,
  diversidad: /diversidad/i,
  lsp: /lengua de se[nñ]as peruana|\blsp\b/i,
  braille: /\bbraille\b/i,
  dua: /dise[nñ]o universal para el aprendizaje|\bdua\b/i,
  pictogramas: /pictograma/i,
  tea: /trastorno del espectro autista|\btea\b/i,
};

function decodeBasicEntities(value = '') {
  return value
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/\s+/g, ' ')
    .trim();
}

function parseAttributes(tag = '') {
  const attrs = {};
  const re = /([^\s=/>]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))/g;
  for (const match of tag.matchAll(re)) {
    attrs[match[1].toLowerCase()] = decodeBasicEntities(match[2] ?? match[3] ?? match[4] ?? '');
  }
  return attrs;
}

function allTags(html, name) {
  return [...html.matchAll(new RegExp(`<${name}\\b[^>]*>`, 'gi'))].map((m) => m[0]);
}

export function analyzeHtml(html, relativePath = 'index.html') {
  const titleMatch = html.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i);
  const title = titleMatch ? decodeBasicEntities(titleMatch[1].replace(/<[^>]+>/g, ' ')) : null;

  let description = null;
  let robots = null;
  for (const tag of allTags(html, 'meta')) {
    const attrs = parseAttributes(tag);
    if ((attrs.name || '').toLowerCase() === 'description' && description === null) description = attrs.content || '';
    if ((attrs.name || '').toLowerCase() === 'robots' && robots === null) robots = attrs.content || '';
  }

  let canonical = null;
  for (const tag of allTags(html, 'link')) {
    const attrs = parseAttributes(tag);
    const rel = (attrs.rel || '').toLowerCase().split(/\s+/);
    if (rel.includes('canonical')) {
      canonical = attrs.href || '';
      break;
    }
  }

  const h1Count = (html.match(/<h1\b/gi) || []).length;
  const noindex = /(^|[,\s])noindex([,\s]|$)/i.test(robots || '');
  const jsonLdTypes = new Set();
  const scripts = [...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)];
  for (const [, attrsText, body] of scripts) {
    const attrs = parseAttributes(`<script ${attrsText}>`);
    if ((attrs.type || '').toLowerCase() !== 'application/ld+json') continue;
    try {
      const data = JSON.parse(body.trim());
      const stack = [data];
      while (stack.length) {
        const node = stack.pop();
        if (Array.isArray(node)) {
          stack.push(...node);
        } else if (node && typeof node === 'object') {
          if (node['@type']) {
            const types = Array.isArray(node['@type']) ? node['@type'] : [node['@type']];
            for (const type of types) jsonLdTypes.add(String(type));
          }
          stack.push(...Object.values(node));
        }
      }
    } catch {
      jsonLdTypes.add('INVALID_JSON_LD');
    }
  }

  const terms = {};
  for (const [key, pattern] of Object.entries(TERM_PATTERNS)) terms[key] = pattern.test(html);

  return {
    path: relativePath.replaceAll('\\', '/'),
    title,
    description,
    canonical,
    robots,
    noindex,
    h1_count: h1Count,
    json_ld_types: [...jsonLdTypes].sort(),
    terms,
  };
}

export function parseSitemapUrls(xml = '') {
  return [...xml.matchAll(/<loc>\s*([^<]+?)\s*<\/loc>/gi)].map((m) => decodeBasicEntities(m[1]));
}

function walkHtml(dir, base = dir, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (['.git', 'node_modules', '_site'].includes(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walkHtml(full, base, out);
    else if (entry.isFile() && entry.name.toLowerCase().endsWith('.html')) out.push(path.relative(base, full));
  }
  return out;
}

function readIfExists(file) {
  return fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : null;
}

export function auditRepository(repoRoot, repoName) {
  const htmlPaths = walkHtml(repoRoot).sort();
  const pages = htmlPaths.map((relative) => analyzeHtml(fs.readFileSync(path.join(repoRoot, relative), 'utf8'), relative));
  const indexable = pages.filter((p) => !p.noindex);
  const sitemapName = repoName === 'crebeucayali.github.io' && fs.existsSync(path.join(repoRoot, 'sitemap-v2.xml'))
    ? 'sitemap-v2.xml'
    : 'sitemap.xml';
  const sitemapContent = readIfExists(path.join(repoRoot, sitemapName));
  const sitemapUrls = sitemapContent ? parseSitemapUrls(sitemapContent) : [];
  const robotsContent = readIfExists(path.join(repoRoot, 'robots.txt'));
  const robotsSitemaps = robotsContent
    ? [...robotsContent.matchAll(/^\s*Sitemap:\s*(\S+)\s*$/gim)].map((m) => m[1])
    : [];

  const missing = {
    title: indexable.filter((p) => !p.title).map((p) => p.path),
    description: indexable.filter((p) => !p.description).map((p) => p.path),
    canonical: indexable.filter((p) => !p.canonical).map((p) => p.path),
    h1: indexable.filter((p) => p.h1_count === 0).map((p) => p.path),
  };

  const invalidCanonicalHost = indexable
    .filter((p) => p.canonical && !p.canonical.startsWith('https://crebeucayali.github.io/'))
    .map((p) => ({ path: p.path, canonical: p.canonical }));

  const termCoverage = {};
  for (const term of Object.keys(TERM_PATTERNS)) termCoverage[term] = indexable.filter((p) => p.terms[term]).length;

  return {
    repo: repoName,
    html_pages: pages.length,
    indexable_candidates: indexable.length,
    noindex_pages: pages.filter((p) => p.noindex).length,
    sitemap: {
      file: sitemapContent ? sitemapName : null,
      urls: sitemapUrls.length,
      entries: sitemapUrls,
    },
    robots: {
      exists: robotsContent !== null,
      host_root_effective: repoName === 'crebeucayali.github.io',
      sitemap_declarations: robotsSitemaps,
    },
    missing,
    invalid_canonical_host: invalidCanonicalHost,
    structured_data_pages: indexable.filter((p) => p.json_ld_types.length > 0).length,
    term_coverage_pages: termCoverage,
    pages,
  };
}

export function auditWorkspace(workspaceRoot) {
  const repositories = [];
  for (const repoName of EXPECTED_REPOS) {
    const repoRoot = path.join(workspaceRoot, repoName);
    if (!fs.existsSync(repoRoot)) throw new Error(`Repositorio faltante en workspace: ${repoName}`);
    repositories.push(auditRepository(repoRoot, repoName));
  }

  const root = repositories.find((r) => r.repo === 'crebeucayali.github.io');
  const totals = {
    repositories: repositories.length,
    html_pages: repositories.reduce((n, r) => n + r.html_pages, 0),
    indexable_candidates: repositories.reduce((n, r) => n + r.indexable_candidates, 0),
    missing_title: repositories.reduce((n, r) => n + r.missing.title.length, 0),
    missing_description: repositories.reduce((n, r) => n + r.missing.description.length, 0),
    missing_canonical: repositories.reduce((n, r) => n + r.missing.canonical.length, 0),
    missing_h1: repositories.reduce((n, r) => n + r.missing.h1.length, 0),
    invalid_canonical_host: repositories.reduce((n, r) => n + r.invalid_canonical_host.length, 0),
  };

  const findings = [];
  if ((root?.sitemap?.urls ?? 0) <= 1) {
    findings.push({ priority: 'MUY_ALTA', code: 'ROOT_SITEMAP_LIMITED', detail: 'El sitemap raíz presenta una cobertura insuficiente del ecosistema EVA.' });
  }
  if (totals.missing_canonical > 0) findings.push({ priority: 'ALTA', code: 'MISSING_CANONICAL', count: totals.missing_canonical });
  if (totals.missing_description > 0) findings.push({ priority: 'ALTA', code: 'MISSING_DESCRIPTION', count: totals.missing_description });
  if (totals.invalid_canonical_host > 0) findings.push({ priority: 'ALTA', code: 'INVALID_CANONICAL_HOST', count: totals.invalid_canonical_host });
  for (const repo of repositories) {
    if (!repo.sitemap.file) findings.push({ priority: 'ALTA', code: 'MISSING_SITEMAP', repo: repo.repo });
    else if (repo.sitemap.urls < repo.indexable_candidates) {
      findings.push({ priority: 'ALTA', code: 'SITEMAP_COVERAGE_REVIEW', repo: repo.repo, sitemap_urls: repo.sitemap.urls, indexable_candidates: repo.indexable_candidates });
    }
    if (repo.repo !== 'crebeucayali.github.io' && repo.robots.exists) {
      findings.push({ priority: 'MEDIA', code: 'SUBDIRECTORY_ROBOTS_INFORMATIONAL', repo: repo.repo, detail: 'El robots.txt del subdirectorio no sustituye al robots.txt del host raíz.' });
    }
  }

  return {
    schema_version: 1,
    fase: 9,
    etapa: 1,
    nombre: 'Auditoría e inventario SEO',
    modo: 'READ_ONLY_SEO_AUDIT',
    generated_at: new Date().toISOString(),
    objective: 'Inventariar señales SEO técnicas de EVA sin modificar repositorios de producto ni Supabase.',
    totals,
    root_discovery: {
      robots_exists: root?.robots?.exists ?? false,
      robots_sitemap_declarations: root?.robots?.sitemap_declarations ?? [],
      root_sitemap_file: root?.sitemap?.file ?? null,
      root_sitemap_urls: root?.sitemap?.urls ?? 0,
    },
    findings,
    repositories,
    guardrails: {
      read_only: true,
      repositorios_eva_modificados: false,
      supabase_modificado: false,
      panel_administrativo_modificado: false,
      correcciones_aplicadas: 0,
    },
  };
}

function main() {
  const workspace = process.argv[2];
  const output = process.argv[3];
  if (!workspace || !output) {
    console.error('Uso: node seo_audit.mjs <workspace-eva> <reporte.json>');
    process.exit(2);
  }
  const report = auditWorkspace(path.resolve(workspace));
  const outputPath = path.resolve(output);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  console.log(JSON.stringify({ totals: report.totals, root_discovery: report.root_discovery, findings: report.findings.length }, null, 2));
}

const current = fileURLToPath(import.meta.url);
if (process.argv[1] && current === path.resolve(process.argv[1])) main();
