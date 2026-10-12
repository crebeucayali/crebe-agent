import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const HOST = 'https://crebeucayali.github.io/';

export const CHILD_SITEMAPS = [
  `${HOST}sitemap-main.xml`,
  `${HOST}accesos-complementarios/sitemap.xml`,
  `${HOST}capacitaciones/sitemap.xml`,
  `${HOST}banco-digital-accesible/sitemap.xml`,
  `${HOST}materiales-educativos-accesibles/sitemap.xml`,
  `${HOST}noti-inclusivos/sitemap.xml`,
  `${HOST}repositorio-accesible/sitemap.xml`,
  `${HOST}DUA-3.0/sitemap.xml`,
];

export const EXPECTED = {
  'crebeucayali.github.io': {
    sitemap: 'sitemap-main.xml',
    urls: [
      `${HOST}`,
      `${HOST}buscar/`,
    ],
  },
  'accesos-complementarios': {
    sitemap: 'sitemap.xml',
    urls: [
      `${HOST}accesos-complementarios/`,
      `${HOST}accesos-complementarios/paginas/nosotros.html`,
      `${HOST}accesos-complementarios/paginas/que-hacemos.html`,
      `${HOST}accesos-complementarios/paginas/contacto.html`,
      `${HOST}accesos-complementarios/paginas/guia-de-uso.html`,
      `${HOST}accesos-complementarios/paginas/lineas-de-accion.html`,
      `${HOST}accesos-complementarios/directorios/directorio-institucional.html`,
      `${HOST}accesos-complementarios/directorios/directorio-ciudadano.html`,
      `${HOST}accesos-complementarios/firma-tu-visita/`,
      `${HOST}accesos-complementarios/mapa-web.html`,
      `${HOST}accesos-complementarios/recursos/galeria.html`,
      `${HOST}accesos-complementarios/recursos/calendario.html`,
      `${HOST}accesos-complementarios/paginas/aviso-legal.html`,
      `${HOST}accesos-complementarios/paginas/politica-privacidad.html`,
      `${HOST}accesos-complementarios/paginas/politica-cookies.html`,
    ],
  },
  capacitaciones: {
    sitemap: 'sitemap.xml',
    urls: [
      `${HOST}capacitaciones/`,
      `${HOST}capacitaciones/primera-jornada.html`,
      `${HOST}capacitaciones/segunda-jornada.html`,
    ],
  },
  'banco-digital-accesible': {
    sitemap: 'sitemap.xml',
    urls: [
      `${HOST}banco-digital-accesible/`,
      `${HOST}banco-digital-accesible/lsp/`,
      `${HOST}banco-digital-accesible/lsp/accesibilidad.html`,
      `${HOST}banco-digital-accesible/lsp/faq.html`,
      `${HOST}banco-digital-accesible/lsp/creditos.html`,
      `${HOST}banco-digital-accesible/braille/`,
      `${HOST}banco-digital-accesible/braille/teoria.html`,
      `${HOST}banco-digital-accesible/braille/accesibilidad.html`,
      `${HOST}banco-digital-accesible/braille/faq.html`,
      `${HOST}banco-digital-accesible/biblioteca/`,
      `${HOST}banco-digital-accesible/biblioteca/criterios.html`,
      `${HOST}banco-digital-accesible/creditos.html`,
    ],
  },
  'materiales-educativos-accesibles': {
    sitemap: 'sitemap.xml',
    urls: [
      `${HOST}materiales-educativos-accesibles/`,
      `${HOST}materiales-educativos-accesibles/generador/generador.html`,
      `${HOST}materiales-educativos-accesibles/generador-lsp/`,
      `${HOST}materiales-educativos-accesibles/apoyos-lsp/generador-lsp.html`,
      `${HOST}materiales-educativos-accesibles/pictogramas/pictogramas.html`,
      `${HOST}materiales-educativos-accesibles/rutinas/rutinas.html`,
      `${HOST}materiales-educativos-accesibles/conciencia-fonologica/conciencia-fonologica.html`,
      `${HOST}materiales-educativos-accesibles/practica-braille/`,
      `${HOST}materiales-educativos-accesibles/practica-braille-opciones/`,
      `${HOST}materiales-educativos-accesibles/practica-braille-v2/`,
      `${HOST}materiales-educativos-accesibles/paginas/privacidad-seguimiento-braille.html`,
    ],
  },
  'noti-inclusivos': {
    sitemap: 'sitemap.xml',
    urls: [
      `${HOST}noti-inclusivos/`,
      `${HOST}noti-inclusivos/articulos/`,
      `${HOST}noti-inclusivos/articulos/cuentos-inclusion-discapacidad/`,
      `${HOST}noti-inclusivos/articulos/lanzamiento-eva/`,
      `${HOST}noti-inclusivos/articulos/natacion-inclusiva-sin-barreras/`,
      `${HOST}noti-inclusivos/articulos/neurodiversidad-del-reconocimiento-a-los-apoyos/`,
      `${HOST}noti-inclusivos/articulos/salud-emergencias-inclusion/`,
      `${HOST}noti-inclusivos/articulos/sindrome-down-y-bioetica/`,
      `${HOST}noti-inclusivos/articulos/transicion-vida-adulta/`,
    ],
  },
  'repositorio-accesible': {
    sitemap: 'sitemap.xml',
    urls: [
      `${HOST}repositorio-accesible/`,
    ],
  },
  'DUA-3.0': {
    sitemap: 'sitemap.xml',
    urls: [
      `${HOST}DUA-3.0/`,
      `${HOST}DUA-3.0/evolucion.html`,
      `${HOST}DUA-3.0/recursos.html`,
    ],
  },
};

export const EXCLUDED = [
  'google09722cd21d5d281a.html',
  '/admin/',
  '/pruebas/',
  '/accesos-complementarios/paginas/mapa-web.html',
  '/accesos-complementarios/recursos/contacto.html',
  '/banco-digital-accesible/biblioteca/recurso.html',
  '/banco-digital-accesible/docs/referencias/',
  '/noti-inclusivos/blog/',
];

export function parseLocs(xml) {
  return [...xml.matchAll(/<loc>\s*([^<]+?)\s*<\/loc>/g)].map((m) => m[1].trim());
}

export function routeFileForUrl(repo, url) {
  if (!url.startsWith(HOST)) throw new Error(`Host no permitido: ${url}`);
  let relative = url.slice(HOST.length);
  if (repo !== 'crebeucayali.github.io') {
    const prefix = `${repo}/`;
    if (!relative.startsWith(prefix)) throw new Error(`URL fuera del repositorio ${repo}: ${url}`);
    relative = relative.slice(prefix.length);
  }
  if (!relative || relative.endsWith('/')) relative += 'index.html';
  return relative;
}

function sorted(values) {
  return [...values].sort((a, b) => a.localeCompare(b));
}

export function auditIndexation(baseDir) {
  const rootDir = path.join(baseDir, 'crebeucayali.github.io');
  const robotsPath = path.join(rootDir, 'robots.txt');
  const indexPath = path.join(rootDir, 'sitemap-v2.xml');
  if (!fs.existsSync(robotsPath)) throw new Error('Falta robots.txt raíz');
  if (!fs.existsSync(indexPath)) throw new Error('Falta sitemap-v2.xml raíz');

  const robots = fs.readFileSync(robotsPath, 'utf8');
  const sitemapDeclarations = robots
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => /^sitemap:/i.test(line))
    .map((line) => line.replace(/^sitemap:\s*/i, ''));
  const rootIndexUrl = `${HOST}sitemap-v2.xml`;
  if (!sitemapDeclarations.includes(rootIndexUrl)) {
    throw new Error('robots.txt no declara el índice central sitemap-v2.xml');
  }

  const indexXml = fs.readFileSync(indexPath, 'utf8');
  if (!/<sitemapindex\b/i.test(indexXml)) throw new Error('sitemap-v2.xml no es sitemapindex');
  const childLocs = parseLocs(indexXml);
  if (JSON.stringify(sorted(childLocs)) !== JSON.stringify(sorted(CHILD_SITEMAPS))) {
    throw new Error('El índice central no contiene exactamente los ocho sitemaps esperados');
  }

  const repositoryResults = [];
  const allUrls = [];
  const missingRouteFiles = [];

  for (const [repo, spec] of Object.entries(EXPECTED)) {
    const repoDir = path.join(baseDir, repo);
    const sitemapPath = path.join(repoDir, spec.sitemap);
    if (!fs.existsSync(sitemapPath)) throw new Error(`Falta ${repo}/${spec.sitemap}`);
    const xml = fs.readFileSync(sitemapPath, 'utf8');
    if (!/<urlset\b/i.test(xml)) throw new Error(`${repo}/${spec.sitemap} no es urlset`);
    const actual = parseLocs(xml);
    if (JSON.stringify(sorted(actual)) !== JSON.stringify(sorted(spec.urls))) {
      throw new Error(`Cobertura inesperada en ${repo}/${spec.sitemap}`);
    }

    for (const url of actual) {
      if (!url.startsWith(HOST)) throw new Error(`URL fuera del host oficial: ${url}`);
      if (EXCLUDED.some((fragment) => url.includes(fragment))) {
        throw new Error(`URL excluida presente en sitemap: ${url}`);
      }
      const routeFile = routeFileForUrl(repo, url);
      if (!fs.existsSync(path.join(repoDir, routeFile))) {
        missingRouteFiles.push({ repo, url, route_file: routeFile });
      }
      allUrls.push(url);
    }

    repositoryResults.push({
      repo,
      sitemap: spec.sitemap,
      urls: actual.length,
      expected_urls: spec.urls.length,
    });
  }

  const duplicates = allUrls.filter((url, index) => allUrls.indexOf(url) !== index);
  if (duplicates.length) throw new Error(`URLs duplicadas entre sitemaps: ${[...new Set(duplicates)].join(', ')}`);
  if (missingRouteFiles.length) {
    throw new Error(`Rutas del sitemap sin archivo fuente: ${JSON.stringify(missingRouteFiles)}`);
  }

  return {
    schema_version: 1,
    fase: 9,
    etapa: 2,
    nombre: 'Arquitectura de indexación',
    modo: 'READ_ONLY_INDEXATION_VERIFY',
    generated_at: new Date().toISOString(),
    root_discovery: {
      robots_exists: true,
      robots_declares_central_index: true,
      central_index: rootIndexUrl,
      child_sitemaps: childLocs.length,
    },
    totals: {
      repositories: Object.keys(EXPECTED).length,
      child_sitemaps: childLocs.length,
      indexed_urls: allUrls.length,
      duplicate_urls: 0,
      missing_route_files: 0,
    },
    repositories: repositoryResults,
    excluded_patterns: EXCLUDED,
    guardrails: {
      read_only: true,
      repositorios_eva_modificados_por_verificador: false,
      supabase_modificado: false,
      panel_administrativo_modificado: false,
      etapa_3_iniciada: false,
    },
  };
}

function main() {
  const [baseDir = '_eva', output = 'reports/fase-9-etapa-2-arquitectura-indexacion.generated.json'] = process.argv.slice(2);
  const report = auditIndexation(baseDir);
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  console.log(JSON.stringify({ root_discovery: report.root_discovery, totals: report.totals }, null, 2));
}

const current = fileURLToPath(import.meta.url);
if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(current)) main();
