import fs from 'fs';
import path from 'path';
import { pathToFileURL } from 'url';
import { chromium } from 'playwright';
import axe from 'axe-core';

export const REPOS = [
  'crebeucayali.github.io',
  'accesos-complementarios',
  'capacitaciones',
  'banco-digital-accesible',
  'materiales-educativos-accesibles',
  'noti-inclusivos',
  'repositorio-accesible',
  'DUA-3.0'
];

export const OVERFLOW_TARGETS = new Set([
  'accesos-complementarios/paginas/contacto.html',
  'accesos-complementarios/recursos/contacto.html',
  'banco-digital-accesible/braille/teoria.html',
  'materiales-educativos-accesibles/generador/generador.html'
]);

export function walkHtml(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === '.git') continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walkHtml(full));
    else if (entry.isFile() && entry.name.endsWith('.html')) out.push(full);
  }
  return out;
}

export function publicUrl(repo, rel) {
  const suffix = rel.replaceAll(path.sep, '/').replace(/index\.html$/, '');
  return repo === 'crebeucayali.github.io'
    ? `https://crebeucayali.github.io/${suffix}`
    : `https://crebeucayali.github.io/${repo}/${suffix}`;
}

export function isAuxiliary(rel) {
  const normalized = rel.replaceAll('\\', '/');
  return /^google[0-9a-f]+\.html$/i.test(normalized) || normalized.startsWith('docs/referencias/');
}

export function evaluateSummary({ loadFailures, contrastNodes, overflowDetail }) {
  const overflowFailures = overflowDetail.filter(item => item.horizontalOverflow);
  const alerts = [];
  if (loadFailures.length > 0) alerts.push(`Páginas no cargadas: ${loadFailures.length}`);
  if (contrastNodes > 0) alerts.push(`Nodos con regresión de contraste: ${contrastNodes}`);
  if (overflowDetail.length !== OVERFLOW_TARGETS.size) {
    alerts.push(`Objetivos de reflujo observados: ${overflowDetail.length}/${OVERFLOW_TARGETS.size}`);
  }
  if (overflowFailures.length > 0) alerts.push(`Objetivos con overflow horizontal: ${overflowFailures.length}`);
  return {
    estado: alerts.length ? 'ALERTA' : 'SIN_REGRESIONES_AUTOMATIZADAS',
    alertas: alerts,
    overflowFailures
  };
}

export async function runMonitor(root = '_eva', output = 'reports/accessibility-monitor/resultado.json') {
  const pages = [];
  for (const repo of REPOS) {
    const repoDir = path.join(root, repo);
    for (const file of walkHtml(repoDir)) {
      const rel = path.relative(repoDir, file).replaceAll(path.sep, '/');
      if (!isAuxiliary(rel)) pages.push({ repo, rel, url: publicUrl(repo, rel) });
    }
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, bypassCSP: true });
  let contrastNodes = 0;
  const contrastDetail = [];
  const overflowDetail = [];
  const loadFailures = [];

  for (const item of pages) {
    const page = await context.newPage();
    try {
      const response = await page.goto(item.url, { waitUntil: 'domcontentloaded', timeout: 15000 });
      if (!response || response.status() >= 400) {
        loadFailures.push({ repo: item.repo, path: item.rel, status: response?.status() ?? null });
        await page.close();
        continue;
      }

      await page.waitForTimeout(400);
      await page.addScriptTag({ content: axe.source });
      const axeResult = await page.evaluate(async () => await axe.run(document, {
        runOnly: { type: 'rule', values: ['color-contrast'] }
      }));
      const nodes = axeResult.violations.reduce((count, violation) => count + violation.nodes.length, 0);
      contrastNodes += nodes;
      if (nodes > 0) {
        contrastDetail.push({
          repo: item.repo,
          path: item.rel,
          nodes,
          violations: axeResult.violations.map(violation => ({
            id: violation.id,
            nodes: violation.nodes.length,
            detail: violation.nodes.map(node => ({
              target: node.target,
              html: node.html,
              failureSummary: node.failureSummary,
              checks: [...(node.any || []), ...(node.all || []), ...(node.none || [])].map(check => ({
                id: check.id,
                message: check.message,
                data: check.data || null
              }))
            }))
          }))
        });
      }

      const key = `${item.repo}/${item.rel}`;
      if (OVERFLOW_TARGETS.has(key)) {
        await page.setViewportSize({ width: 320, height: 800 });
        await page.waitForTimeout(150);
        const dimensions = await page.evaluate(() => ({
          clientWidth: document.documentElement.clientWidth,
          scrollWidth: document.documentElement.scrollWidth
        }));
        overflowDetail.push({
          repo: item.repo,
          path: item.rel,
          ...dimensions,
          horizontalOverflow: dimensions.scrollWidth > dimensions.clientWidth + 2
        });
      }
    } catch (error) {
      loadFailures.push({ repo: item.repo, path: item.rel, error: String(error.message || error) });
    }
    await page.close();
  }

  await context.close();
  await browser.close();

  const summary = evaluateSummary({ loadFailures, contrastNodes, overflowDetail });
  const report = {
    schema_version: 1,
    fase: 8,
    etapa: 8,
    nombre: 'Verificación y monitoreo recurrente de accesibilidad',
    modo: 'READ_ONLY_RECURRENT_MONITOR',
    estado: summary.estado,
    alertas: summary.alertas,
    paginas_funcionales_observadas: pages.length,
    paginas_no_cargadas: loadFailures.length,
    contraste: {
      nodos_regresion: contrastNodes,
      paginas_afectadas: contrastDetail.length,
      detalle: contrastDetail
    },
    reflujo: {
      targets_esperados: OVERFLOW_TARGETS.size,
      targets_verificados: overflowDetail.length,
      targets_con_overflow: summary.overflowFailures.length,
      detalle: overflowDetail
    },
    revision_manual: {
      contratos_sin_fallo_confirmado_pendientes: 22,
      certificacion_wcag_completa: false,
      nota: 'El monitor automatizado cubre regresiones de contraste, carga y los cuatro objetivos de reflujo diagnosticados. No convierte en fallos los contratos pendientes de revisión manual ni certifica cumplimiento WCAG integral.'
    },
    guardrails: {
      repositorios_eva_modificados_por_monitor: false,
      supabase_modificado: false,
      solo_lectura: true
    }
  };

  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report, null, 2));
  if (summary.alertas.length) process.exitCode = 1;
  return report;
}

const invokedDirectly = process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;
if (invokedDirectly) {
  await runMonitor(process.argv[2] || '_eva', process.argv[3] || 'reports/accessibility-monitor/resultado.json');
}
