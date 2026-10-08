import fs from 'fs';
import path from 'path';
import { chromium } from 'playwright';
import axe from 'axe-core';

const REPOS = [
  'crebeucayali.github.io',
  'accesos-complementarios',
  'capacitaciones',
  'banco-digital-accesible',
  'materiales-educativos-accesibles',
  'noti-inclusivos',
  'repositorio-accesible',
  'DUA-3.0'
];

const AXE_TO_CONTRACTS = {
  'label': ['A11Y-CON-005'],
  'select-name': ['A11Y-CON-005'],
  'input-button-name': ['A11Y-CON-005'],
  'button-name': ['A11Y-CON-004'],
  'link-name': ['A11Y-CON-004'],
  'aria-allowed-attr': ['A11Y-CON-019'],
  'aria-allowed-role': ['A11Y-CON-019'],
  'aria-command-name': ['A11Y-CON-019'],
  'aria-conditional-attr': ['A11Y-CON-019'],
  'aria-deprecated-role': ['A11Y-CON-019'],
  'aria-hidden-body': ['A11Y-CON-019'],
  'aria-hidden-focus': ['A11Y-CON-019'],
  'aria-input-field-name': ['A11Y-CON-019'],
  'aria-meter-name': ['A11Y-CON-019'],
  'aria-progressbar-name': ['A11Y-CON-019'],
  'aria-prohibited-attr': ['A11Y-CON-019'],
  'aria-required-attr': ['A11Y-CON-019'],
  'aria-required-children': ['A11Y-CON-019'],
  'aria-required-parent': ['A11Y-CON-019'],
  'aria-roles': ['A11Y-CON-019'],
  'aria-toggle-field-name': ['A11Y-CON-019'],
  'aria-tooltip-name': ['A11Y-CON-019'],
  'aria-valid-attr-value': ['A11Y-CON-019'],
  'aria-valid-attr': ['A11Y-CON-019'],
  'heading-order': ['A11Y-CON-007'],
  'list': ['A11Y-CON-008'],
  'listitem': ['A11Y-CON-008'],
  'definition-list': ['A11Y-CON-008'],
  'html-has-lang': ['A11Y-CON-009'],
  'html-lang-valid': ['A11Y-CON-009'],
  'document-title': ['A11Y-CON-010'],
  'landmark-one-main': ['A11Y-CON-011'],
  'region': ['A11Y-CON-011'],
  'landmark-unique': ['A11Y-CON-012'],
  'duplicate-id-aria': ['A11Y-CON-019'],
  'table-duplicate-name': ['A11Y-CON-021'],
  'td-headers-attr': ['A11Y-CON-021'],
  'th-has-data-cells': ['A11Y-CON-021'],
  'scope-attr-valid': ['A11Y-CON-021'],
  'color-contrast': ['A11Y-CON-023']
};

function walkHtml(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === '.git') continue;
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walkHtml(p));
    else if (entry.isFile() && entry.name.endsWith('.html')) out.push(p);
  }
  return out;
}

function publicUrl(repo, rel) {
  const suffix = rel.replaceAll(path.sep, '/').replace(/index\.html$/, '');
  if (repo === 'crebeucayali.github.io') return `https://crebeucayali.github.io/${suffix}`;
  return `https://crebeucayali.github.io/${repo}/${suffix}`;
}

function isAuxiliary(rel) {
  const n = rel.replaceAll('\\', '/');
  return /^google[0-9a-f]+\.html$/i.test(n) || n.startsWith('docs/referencias/');
}

const root = process.argv[2] || '_eva';
const output = process.argv[3] || 'reports/fase-8-etapa-5-pruebas-controladas.generated.json';
const pages = [];
for (const repo of REPOS) {
  const repoDir = path.join(root, repo);
  for (const file of walkHtml(repoDir)) {
    const rel = path.relative(repoDir, file);
    pages.push({ repo, rel, url: publicUrl(repo, rel), auxiliary: isAuxiliary(rel) });
  }
}

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, bypassCSP: true });
const results = [];

for (const item of pages) {
  const page = await context.newPage();
  const row = { ...item, loaded: false, testComplete: false, status: null, finalUrl: '', axe: [], metrics: {}, notes: [] };
  try {
    const response = await page.goto(item.url, { waitUntil: 'domcontentloaded', timeout: 15000 });
    row.status = response ? response.status() : null;
    row.loaded = !!response && response.status() < 400;
    if (!row.loaded) {
      row.notes.push('La URL no cargo satisfactoriamente; no se interpreta como fallo de accesibilidad en esta etapa.');
      results.push(row);
      await page.close();
      continue;
    }

    // Permite que redirecciones de compatibilidad terminen antes de auditar el documento final.
    await page.waitForTimeout(500);
    await page.waitForLoadState('domcontentloaded', { timeout: 5000 }).catch(() => {});
    row.finalUrl = page.url();

    await page.addScriptTag({ content: axe.source });
    const axeResult = await page.evaluate(async () => {
      return await axe.run(document, {
        runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'] }
      });
    });
    row.axe = axeResult.violations.map(v => ({
      id: v.id,
      impact: v.impact,
      nodes: v.nodes.length,
      contracts: AXE_TO_CONTRACTS[v.id] || []
    }));

    row.metrics = await page.evaluate(() => {
      const focusable = [...document.querySelectorAll('a[href],button,input:not([type=hidden]),select,textarea,[tabindex]:not([tabindex="-1"])')]
        .filter(el => !el.disabled && getComputedStyle(el).visibility !== 'hidden' && getComputedStyle(el).display !== 'none');
      const tables = [...document.querySelectorAll('table')];
      const media = [...document.querySelectorAll('video,audio')];
      const dialogs = [...document.querySelectorAll('dialog,[role="dialog"],[role="alertdialog"]')];
      const liveRegions = [...document.querySelectorAll('[aria-live],[role="status"],[role="alert"]')];
      return {
        focusable: focusable.length,
        forms: document.querySelectorAll('form').length,
        tables: tables.length,
        tablesWithHeaders: tables.filter(t => t.querySelector('th')).length,
        multimedia: media.length,
        dialogs: dialogs.length,
        liveRegions: liveRegions.length,
        lang: document.documentElement.lang || '',
        title: document.title || ''
      };
    });

    if (row.metrics.focusable > 0) {
      await page.keyboard.press('Tab');
      const firstFocus = await page.evaluate(() => {
        const el = document.activeElement;
        if (!el || el === document.body) return { reached: false };
        const cs = getComputedStyle(el);
        return {
          reached: true,
          tag: el.tagName,
          id: el.id || '',
          outlineStyle: cs.outlineStyle,
          outlineWidth: cs.outlineWidth,
          boxShadow: cs.boxShadow
        };
      });
      row.metrics.keyboardFirstTab = firstFocus;
    }

    await page.setViewportSize({ width: 320, height: 800 });
    await page.waitForTimeout(100);
    row.metrics.mobile = await page.evaluate(() => ({
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2
    }));
    row.testComplete = true;
  } catch (error) {
    row.notes.push(`Error de prueba controlada: ${String(error.message || error)}`);
  }
  results.push(row);
  await page.close();
}

await context.close();
await browser.close();

const pendingIds = [
  'A11Y-CON-002','A11Y-CON-004','A11Y-CON-005','A11Y-CON-006','A11Y-CON-007','A11Y-CON-008','A11Y-CON-009','A11Y-CON-010',
  'A11Y-CON-011','A11Y-CON-012','A11Y-CON-013','A11Y-CON-014','A11Y-CON-015','A11Y-CON-016','A11Y-CON-017','A11Y-CON-018',
  'A11Y-CON-019','A11Y-CON-020','A11Y-CON-021','A11Y-CON-022','A11Y-CON-023','A11Y-CON-024','A11Y-CON-025','A11Y-CON-026','A11Y-CON-027','A11Y-CON-028'
];
const contractEvidence = {};
for (const id of pendingIds) contractEvidence[id] = { axeViolations: 0, pages: [], status: 'REQUIERE_DIAGNOSTICO_O_REVISION_MANUAL' };

for (const row of results.filter(r => r.testComplete)) {
  for (const v of row.axe) {
    for (const id of v.contracts || []) {
      if (!contractEvidence[id]) continue;
      contractEvidence[id].axeViolations += v.nodes;
      if (contractEvidence[id].pages.length < 20) contractEvidence[id].pages.push(`${row.repo}/${row.rel}`);
    }
  }
}

for (const ev of Object.values(contractEvidence)) {
  if (ev.axeViolations > 0) ev.status = 'INCUMPLIMIENTO_CONFIRMADO_AUTOMATIZADO';
}

const completedFunctional = results.filter(r => r.loaded && r.testComplete && !r.auxiliary);
const incompleteFunctional = results.filter(r => !r.auxiliary && (!r.loaded || !r.testComplete));
const keyboardCandidates = completedFunctional.filter(r => r.metrics.focusable > 0);
const keyboardUnreached = keyboardCandidates.filter(r => !r.metrics.keyboardFirstTab?.reached);
contractEvidence['A11Y-CON-013'] = {
  pagesWithFocusable: keyboardCandidates.length,
  pagesFirstTabWithoutFocus: keyboardUnreached.length,
  incompleteFunctionalPages: incompleteFunctional.length,
  status: keyboardCandidates.length > 0 && keyboardUnreached.length === 0 && incompleteFunctional.length === 0
    ? 'EVIDENCIA_FAVORABLE_CONTROLADA'
    : (keyboardUnreached.length > 0 ? 'REQUIERE_DIAGNOSTICO' : 'REQUIERE_DIAGNOSTICO_O_REVISION_MANUAL')
};

const overflow = completedFunctional.filter(r => r.metrics.mobile?.horizontalOverflow);
contractEvidence['A11Y-CON-025'] = {
  pagesChecked: completedFunctional.length,
  pagesWithHorizontalOverflowAt320: overflow.length,
  incompleteFunctionalPages: incompleteFunctional.length,
  pages: overflow.slice(0, 30).map(r => `${r.repo}/${r.rel}`),
  status: overflow.length > 0
    ? 'REQUIERE_DIAGNOSTICO'
    : (completedFunctional.length > 0 && incompleteFunctional.length === 0 ? 'EVIDENCIA_FAVORABLE_CONTROLADA' : 'REQUIERE_DIAGNOSTICO_O_REVISION_MANUAL')
};

const tables = completedFunctional.reduce((n, r) => n + (r.metrics.tables || 0), 0);
const multimedia = completedFunctional.reduce((n, r) => n + (r.metrics.multimedia || 0), 0);
if (incompleteFunctional.length === 0 && tables === 0) {
  contractEvidence['A11Y-CON-021'].status = 'NO_APLICA_EN_UNIVERSO_OBSERVADO';
  contractEvidence['A11Y-CON-022'].status = 'NO_APLICA_EN_UNIVERSO_OBSERVADO';
}
if (incompleteFunctional.length === 0 && multimedia === 0) {
  contractEvidence['A11Y-CON-027'].status = 'NO_APLICA_EN_UNIVERSO_OBSERVADO';
}

const summary = {};
for (const ev of Object.values(contractEvidence)) summary[ev.status] = (summary[ev.status] || 0) + 1;

const report = {
  schema_version: 2,
  fase: 8,
  etapa: 5,
  nombre: 'Pruebas controladas de accesibilidad',
  modo: 'READ_ONLY_CONTROLLED_BROWSER_TESTS',
  referencia_tecnica: 'WCAG_2_2_AA',
  orden_pruebas: ['P0','P1','P2'],
  paginas_observadas: pages.length,
  paginas_funcionales_completamente_probadas: completedFunctional.length,
  paginas_funcionales_incompletas: incompleteFunctional.length,
  paginas_auxiliares: results.filter(r => r.auxiliary).length,
  paginas_no_cargadas: results.filter(r => !r.loaded).length,
  tablas_observadas: tables,
  multimedia_observada: multimedia,
  contratos: contractEvidence,
  resumen_estados: summary,
  resultados_paginas: results,
  guardrails: {
    repositorios_eva_modificados: false,
    supabase_modificado: false,
    correcciones_aplicadas: 0,
    severidades_asignadas: 0,
    diagnostico_tecnico_etapa_6_iniciado: false
  }
};

fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({
  paginas: pages.length,
  funcionales_completamente_probadas: completedFunctional.length,
  funcionales_incompletas: incompleteFunctional.length,
  resumen: summary
}, null, 2));
