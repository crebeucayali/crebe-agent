import fs from 'node:fs/promises';

export const ROOT = 'https://crebeucayali.github.io';
export const SITEMAP_INDEX = `${ROOT}/sitemap-v2.xml`;
export const EXPECTED_CHILD_SITEMAPS = [
  `${ROOT}/sitemap-main.xml`,
  `${ROOT}/accesos-complementarios/sitemap.xml`,
  `${ROOT}/capacitaciones/sitemap.xml`,
  `${ROOT}/banco-digital-accesible/sitemap.xml`,
  `${ROOT}/materiales-educativos-accesibles/sitemap.xml`,
  `${ROOT}/noti-inclusivos/sitemap.xml`,
  `${ROOT}/repositorio-accesible/sitemap.xml`,
  `${ROOT}/DUA-3.0/sitemap.xml`,
];

export function extractLocs(xml) {
  return [...String(xml || '').matchAll(/<loc>\s*([^<]+?)\s*<\/loc>/gi)].map((m) => m[1].trim());
}

export function inspectRobots(text) {
  const value = String(text || '');
  return {
    allows_root: /(?:^|\n)\s*Allow:\s*\/\s*(?:\n|$)/i.test(value),
    sitemap_declared: /Sitemap:\s*https:\/\/crebeucayali\.github\.io\/sitemap-v2\.xml/i.test(value),
  };
}

async function getText(url) {
  const response = await fetch(url, { redirect: 'follow', headers: { 'User-Agent': 'crebe-agent-seo-monitor' } });
  return { status: response.status, ok: response.ok, text: await response.text() };
}

async function checkUrl(url) {
  const response = await fetch(url, { redirect: 'follow', headers: { 'User-Agent': 'crebe-agent-seo-monitor' } });
  return { url, status: response.status, reachable: response.status >= 200 && response.status < 400 };
}

export async function runMonitor() {
  const robotsResponse = await getText(`${ROOT}/robots.txt`);
  const robots = { http_status: robotsResponse.status, ...inspectRobots(robotsResponse.text) };

  const indexResponse = await getText(SITEMAP_INDEX);
  const childSitemaps = extractLocs(indexResponse.text);
  const missingChildSitemaps = EXPECTED_CHILD_SITEMAPS.filter((url) => !childSitemaps.includes(url));

  const sitemapChecks = [];
  const officialUrls = new Set();
  for (const sitemapUrl of EXPECTED_CHILD_SITEMAPS) {
    const result = await getText(sitemapUrl);
    const urls = result.ok ? extractLocs(result.text) : [];
    urls.forEach((url) => officialUrls.add(url));
    sitemapChecks.push({ url: sitemapUrl, status: result.status, reachable: result.ok, url_count: urls.length });
  }

  const pageChecks = [];
  for (const url of officialUrls) pageChecks.push(await checkUrl(url));

  const alerts = [];
  if (robots.http_status !== 200) alerts.push('robots_unavailable');
  if (!robots.allows_root) alerts.push('robots_root_not_allowed');
  if (!robots.sitemap_declared) alerts.push('robots_sitemap_not_declared');
  if (indexResponse.status !== 200) alerts.push('sitemap_index_unavailable');
  if (missingChildSitemaps.length) alerts.push('missing_child_sitemaps');
  for (const sitemap of sitemapChecks) if (!sitemap.reachable) alerts.push(`sitemap_unreachable:${sitemap.url}`);
  for (const page of pageChecks) if (!page.reachable) alerts.push(`page_unreachable:${page.url}`);
  if (officialUrls.size !== 56) alerts.push(`official_url_count:${officialUrls.size}`);

  return {
    schema_version: 1,
    fase: 9,
    etapa: 8,
    nombre: 'Monitoreo SEO',
    modo: 'READ_ONLY_SEO_MONITOR',
    checked_at: new Date().toISOString(),
    totals: {
      expected_child_sitemaps: EXPECTED_CHILD_SITEMAPS.length,
      child_sitemaps_present: EXPECTED_CHILD_SITEMAPS.length - missingChildSitemaps.length,
      official_urls: officialUrls.size,
      reachable_official_urls: pageChecks.filter((x) => x.reachable).length,
      alerts: alerts.length,
    },
    robots,
    sitemap_index: { http_status: indexResponse.status, missing_child_sitemaps: missingChildSitemaps },
    sitemap_checks: sitemapChecks,
    page_failures: pageChecks.filter((x) => !x.reachable),
    alerts,
    guardrails: {
      read_only: true,
      repositorios_eva_modificados: false,
      supabase_modificado: false,
      panel_administrativo_modificado: false,
      indexacion_forzada: false,
    },
  };
}

async function main() {
  const output = process.argv[2] || 'reports/seo-monitor/resultado.json';
  const report = await runMonitor();
  await fs.mkdir(output.split('/').slice(0, -1).join('/') || '.', { recursive: true });
  await fs.writeFile(output, JSON.stringify(report, null, 2) + '\n', 'utf8');
  console.log(JSON.stringify({ totals: report.totals, alerts: report.alerts }, null, 2));
  if (report.alerts.length) process.exitCode = 1;
}

if (import.meta.url === `file://${process.argv[1]}`) main();
