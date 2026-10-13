import fs from 'node:fs/promises';

export const TARGETS = [
  ['crebeucayali.github.io', 'https://crebeucayali.github.io/'],
  ['accesos-complementarios', 'https://crebeucayali.github.io/accesos-complementarios/'],
  ['capacitaciones', 'https://crebeucayali.github.io/capacitaciones/'],
  ['banco-digital-accesible', 'https://crebeucayali.github.io/banco-digital-accesible/'],
  ['materiales-educativos-accesibles', 'https://crebeucayali.github.io/materiales-educativos-accesibles/'],
  ['noti-inclusivos', 'https://crebeucayali.github.io/noti-inclusivos/'],
  ['repositorio-accesible', 'https://crebeucayali.github.io/repositorio-accesible/'],
  ['DUA-3.0', 'https://crebeucayali.github.io/DUA-3.0/'],
];

export function inspectRepository(meta, expectedUrl) {
  const homepage = String(meta?.homepage || '').trim();
  return {
    public: meta?.private === false,
    archived: meta?.archived === true,
    pages_enabled: meta?.has_pages === true,
    homepage,
    homepage_matches_expected: homepage.replace(/\/$/, '') === expectedUrl.replace(/\/$/, ''),
    description_present: Boolean(String(meta?.description || '').trim()),
    topics_count: Array.isArray(meta?.topics) ? meta.topics.length : 0,
  };
}

export function inspectRobots(text) {
  const value = String(text || '');
  return {
    allows_root: /(?:^|\n)\s*Allow:\s*\/\s*(?:\n|$)/i.test(value),
    sitemap_declared: /Sitemap:\s*https:\/\/crebeucayali\.github\.io\/sitemap-v2\.xml/i.test(value),
  };
}

export function inspectSitemap(text) {
  const value = String(text || '');
  const expected = [
    'https://crebeucayali.github.io/sitemap-main.xml',
    'https://crebeucayali.github.io/accesos-complementarios/sitemap.xml',
    'https://crebeucayali.github.io/capacitaciones/sitemap.xml',
    'https://crebeucayali.github.io/banco-digital-accesible/sitemap.xml',
    'https://crebeucayali.github.io/materiales-educativos-accesibles/sitemap.xml',
    'https://crebeucayali.github.io/noti-inclusivos/sitemap.xml',
    'https://crebeucayali.github.io/repositorio-accesible/sitemap.xml',
    'https://crebeucayali.github.io/DUA-3.0/sitemap.xml',
  ];
  const missing = expected.filter((url) => !value.includes(`<loc>${url}</loc>`));
  return { expected_entries: expected.length, missing_entries: missing };
}

async function getText(url, options = {}) {
  const response = await fetch(url, { redirect: 'follow', ...options });
  return { status: response.status, ok: response.ok, text: await response.text() };
}

export async function runVerification() {
  const repositories = [];
  for (const [name, expectedUrl] of TARGETS) {
    const api = await getText(`https://api.github.com/repos/crebeucayali/${name}`, {
      headers: { Accept: 'application/vnd.github+json', 'User-Agent': 'crebe-agent-seo-stage-7' },
    });
    if (!api.ok) {
      repositories.push({ name, expected_url: expectedUrl, metadata_http_status: api.status, metadata_error: true });
      continue;
    }
    const meta = JSON.parse(api.text);
    const page = await fetch(expectedUrl, { redirect: 'follow' });
    repositories.push({
      name,
      expected_url: expectedUrl,
      metadata_http_status: api.status,
      page_http_status: page.status,
      page_reachable: page.status >= 200 && page.status < 400,
      ...inspectRepository(meta, expectedUrl),
    });
  }

  const robotsResponse = await getText('https://crebeucayali.github.io/robots.txt');
  const sitemapResponse = await getText('https://crebeucayali.github.io/sitemap-v2.xml');
  const robots = { http_status: robotsResponse.status, ...inspectRobots(robotsResponse.text) };
  const sitemap = { http_status: sitemapResponse.status, ...inspectSitemap(sitemapResponse.text) };

  const requiredFailures = [];
  for (const repo of repositories) {
    if (repo.metadata_error) requiredFailures.push(`${repo.name}:metadata_unavailable`);
    if (repo.public === false) requiredFailures.push(`${repo.name}:not_public`);
    if (repo.archived === true) requiredFailures.push(`${repo.name}:archived`);
    if (repo.pages_enabled === false) requiredFailures.push(`${repo.name}:pages_disabled`);
    if (repo.page_reachable === false) requiredFailures.push(`${repo.name}:page_unreachable`);
  }
  if (robots.http_status !== 200) requiredFailures.push('robots:http_status');
  if (!robots.allows_root) requiredFailures.push('robots:root_not_allowed');
  if (!robots.sitemap_declared) requiredFailures.push('robots:sitemap_not_declared');
  if (sitemap.http_status !== 200) requiredFailures.push('sitemap:http_status');
  if (sitemap.missing_entries.length) requiredFailures.push('sitemap:missing_entries');

  return {
    schema_version: 1,
    fase: 9,
    etapa: 7,
    nombre: 'Buscadores y repositorios',
    modo: 'READ_ONLY_SEARCH_REPOSITORY_VERIFY',
    fecha: new Date().toISOString(),
    repositories,
    robots,
    sitemap,
    totals: {
      repositories: repositories.length,
      public_repositories: repositories.filter((r) => r.public).length,
      pages_enabled: repositories.filter((r) => r.pages_enabled).length,
      pages_reachable: repositories.filter((r) => r.page_reachable).length,
      homepage_matches_expected: repositories.filter((r) => r.homepage_matches_expected).length,
      descriptions_present: repositories.filter((r) => r.description_present).length,
      repositories_with_topics: repositories.filter((r) => (r.topics_count || 0) > 0).length,
      required_failures: requiredFailures.length,
    },
    required_failures: requiredFailures,
    external_search_consoles: {
      google_search_console_submission_performed: false,
      bing_webmaster_submission_performed: false,
      brave_manual_submission_performed: false,
      indexation_forced: false,
      note: 'La etapa verifica señales públicas y configuración técnica. No simula ni fuerza envíos que requieren consolas o credenciales externas.'
    },
    guardrails: {
      read_only: true,
      repositorios_eva_modificados_por_verificador: false,
      supabase_modificado: false,
      panel_administrativo_modificado: false,
      contenido_eva_modificado: false,
      etapa_8_iniciada: false
    }
  };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const output = process.argv[2] || 'reports/fase-9-etapa-7-buscadores-repositorios.generated.json';
  const report = await runVerification();
  await fs.mkdir(new URL('./reports/', import.meta.url), { recursive: true }).catch(() => {});
  await fs.writeFile(output, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  console.log(JSON.stringify({ totals: report.totals, required_failures: report.required_failures }, null, 2));
  if (report.required_failures.length) process.exitCode = 1;
}
