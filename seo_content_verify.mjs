import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { EXPECTED, routeFileForUrl } from './seo_indexation_verify.mjs';
import { analyzeHtml } from './seo_audit.mjs';

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

export function visibleText(html = '') {
  return decodeBasicEntities(
    html
      .replace(/<script\b[\s\S]*?<\/script>/gi, ' ')
      .replace(/<style\b[\s\S]*?<\/style>/gi, ' ')
      .replace(/<[^>]+>/g, ' '),
  );
}

export function h1Texts(html = '') {
  return [...html.matchAll(/<h1\b[^>]*>([\s\S]*?)<\/h1>/gi)]
    .map((match) => decodeBasicEntities(match[1].replace(/<[^>]+>/g, ' ')));
}

export function inspectContent(repo, url, file, html) {
  const analysis = analyzeHtml(html, file);
  const headings = h1Texts(html);
  const text = visibleText(html);
  const semanticTerms = Object.entries(analysis.terms)
    .filter(([, present]) => present)
    .map(([term]) => term);

  const errors = [];
  if (headings.length === 0) errors.push('missing_h1');
  if (headings.length > 1) errors.push('multiple_h1');
  if (headings.some((heading) => !heading)) errors.push('empty_h1');
  if (text.length < 120) errors.push('thin_visible_content');
  if (semanticTerms.length === 0) errors.push('missing_semantic_terms');

  return {
    repo,
    url,
    file,
    h1_count: headings.length,
    h1: headings,
    visible_text_chars: text.length,
    semantic_terms: semanticTerms,
    status: errors.length ? 'FAIL' : 'PASS',
    errors,
  };
}

export function auditContent(baseDir) {
  const pages = [];
  for (const [repo, spec] of Object.entries(EXPECTED)) {
    for (const url of spec.urls) {
      const file = routeFileForUrl(repo, url);
      const source = path.join(baseDir, repo, file);
      if (!fs.existsSync(source)) {
        pages.push({ repo, url, file, h1_count: 0, h1: [], visible_text_chars: 0, semantic_terms: [], status: 'FAIL', errors: ['missing_route_file'] });
        continue;
      }
      pages.push(inspectContent(repo, url, file, fs.readFileSync(source, 'utf8')));
    }
  }

  const count = (predicate) => pages.filter(predicate).length;
  return {
    schema_version: 1,
    fase: 9,
    etapa: 5,
    nombre: 'SEO de contenidos',
    modo: 'READ_ONLY_CONTENT_VERIFY',
    totals: {
      repositories: Object.keys(EXPECTED).length,
      official_urls: pages.length,
      missing_h1: count((page) => page.h1_count === 0),
      multiple_h1: count((page) => page.h1_count > 1),
      empty_h1: count((page) => page.h1.some((heading) => !heading)),
      under_120_visible_chars: count((page) => page.visible_text_chars < 120),
      without_semantic_terms: count((page) => page.semantic_terms.length === 0),
      failing_pages: count((page) => page.status !== 'PASS'),
    },
    pages,
    guardrails: {
      read_only: true,
      repositorios_eva_modificados_por_verificador: false,
      contenido_reescrito_por_verificador: false,
      supabase_modificado: false,
      panel_administrativo_modificado: false,
      archivos_accesibilidad_modificados: false,
      etapa_6_iniciada: false,
    },
  };
}

function main() {
  const [, , baseDir = '_eva', output = 'reports/fase-9-etapa-5-seo-contenidos.generated.json'] = process.argv;
  const report = auditContent(baseDir);
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  console.log(JSON.stringify(report.totals));
  if (report.totals.failing_pages > 0) process.exitCode = 1;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) main();
