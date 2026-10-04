"""Mediciones de portadas públicas sin sesión, interacciones ni acceso al backend."""
import argparse
import asyncio
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
from audit import read, write_report

VIEWPORTS = {'desktop': {'width': 1440, 'height': 900}, 'mobile': {'width': 390, 'height': 844}}


def allowed_request(url, method):
    parsed = urlsplit(url)
    return parsed.scheme == 'https' and parsed.hostname == 'crebeucayali.github.io' and method in {'GET', 'HEAD'}


def evaluate(page, rules):
    findings = []
    def add(rule, level, description, evidence):
        findings.append({'repo': page['repo'], 'viewport': page['viewport'], 'rule': rule, 'level': level, 'description': description, 'evidence': evidence})
    if page.get('error'):
        add('page.unverified', 'no_verificado', 'La página no pudo medirse.', page['error'])
        return findings
    if page.get('http_status') != 200:
        add('page.http', 'inconsistencia', 'La portada respondió HTTP ' + str(page.get('http_status')) + '.', {})
    m = page['measurements']
    if m['horizontal_overflow'] > 2:
        add('layout.overflow', 'inconsistencia', 'Desbordamiento horizontal de ' + str(m['horizontal_overflow']) + ' px.', {'viewport': page['viewport'], 'overflow_px': m['horizontal_overflow']})
    expected = rules['navigation_font_px'][page['viewport']]
    if not m['nav_links']:
        add('navigation.unmeasured', 'no_verificado', 'No se encontraron enlaces visibles con el selector de navegación.', {'selector': page['selectors']['links']})
    mismatches = [link for link in m['nav_links'] if abs(float(link['fontSize'].replace('px', '')) - expected) > rules['navigation_font_tolerance_px']]
    if mismatches:
        add('navigation.font', 'inconsistencia', 'Hay enlaces de navegación fuera del tamaño previsto de ' + str(expected) + ' px.', mismatches)
    lo, hi = rules['navigation_weight_range']
    weights = [link for link in m['nav_links'] if link['fontWeight'].isdigit() and not lo <= int(link['fontWeight']) <= hi]
    if weights:
        add('navigation.weight', 'revision', 'Hay pesos tipográficos fuera de la franja de 500 a 700.', weights)
    if page['viewport'] == 'desktop' and m.get('nav'):
        minimum = m['nav']['minHeight']
        if minimum.endswith('px') and float(minimum[:-2]) > 0 and abs(float(minimum[:-2]) - rules['header_height_reference_px']) > 1:
            add('navigation.minimum_height', 'revision', 'La altura mínima CSS de la franja de navegación difiere de 74 px.', m['nav'])
    for share in m['share_labels']:
        if share != rules['share_label']:
            add('share.label', 'inconsistencia', 'Etiqueta visible de compartir: "' + share + '"; se esperaba "' + rules['share_label'] + '".', {'label': share})
    return findings


DOM_MEASURE = r'''(selectors) => {
  const visible = el => !!el && getComputedStyle(el).visibility !== 'hidden' && el.getClientRects().length > 0;
  const sample = el => {
    if (!el) return null;
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return {height: Math.round(r.height * 100) / 100, width: Math.round(r.width * 100) / 100,
      minHeight: s.minHeight, fontSize: s.fontSize, fontWeight: s.fontWeight,
      fontFamily: s.fontFamily, paddingTop: s.paddingTop, paddingBottom: s.paddingBottom,
      text: el.innerText.trim().replace(/\s+/g, ' ').slice(0, 150)};
  };
  const nav = document.querySelector(selectors.nav);
  const footer = document.querySelector(selectors.footer);
  return {
    nav: sample(nav),
    nav_links: [...document.querySelectorAll(selectors.links)].filter(visible).map(el => ({...sample(el), href: el.href})),
    footer: sample(footer), footer_body: sample(footer && footer.querySelector('p')),
    footer_heading: sample(footer && footer.querySelector('h2,h3,.crebe-footer-heading')),
    footer_links: footer ? [...footer.querySelectorAll('a')].map(a => ({text:a.innerText.trim(), href:a.href})) : [],
    share_labels: [...document.querySelectorAll('[data-compartir-facebook], .compartir-eva a, .compartir-eva button')].filter(visible).map(el => el.innerText.trim().replace(/\s+/g,' ')),
    horizontal_overflow: Math.max(0, document.documentElement.scrollWidth - innerWidth)
  };
}'''


async def inspect(browser, repo, viewport, rules, output):
    selectors = rules['selectors'].get(repo['repo'], rules['selectors']['default'])
    record = {'repo': repo['repo'], 'viewport': viewport, 'selectors': selectors, 'url': repo['pages_url_expected'], 'source_commit': repo['commit'], 'blocked_requests': 0}
    context = await browser.new_context(viewport=VIEWPORTS[viewport], service_workers='block', accept_downloads=False)
    async def route_handler(route):
        request = route.request
        if allowed_request(request.url, request.method):
            await route.continue_()
        else:
            record['blocked_requests'] += 1
            await route.abort()
    await context.route('**/*', route_handler)
    # No permitir sockets a servicios externos.
    async def close_socket(route):
        await route.close()
    await context.route_web_socket('**/*', close_socket)
    page = await context.new_page()
    try:
        response = await page.goto(repo['pages_url_expected'], wait_until='domcontentloaded', timeout=35000)
        record['http_status'] = response.status if response else None
        await page.wait_for_timeout(1200)
        record['measurements'] = await page.evaluate(DOM_MEASURE, selectors)
        screenshot = repo['repo'] + '-' + viewport + '.png'
        await page.screenshot(path=str(output / 'screenshots' / screenshot), full_page=False, animations='disabled')
        record['screenshot'] = 'screenshots/' + screenshot
    except Exception as exc:
        record['error'] = type(exc).__name__
    finally:
        await context.close()
    return record


async def run(args):
    from playwright.async_api import async_playwright
    repos = read(args.inventory / 'repositories.json')
    static = read(args.output / 'consistency.json')
    rules = read(args.rules)
    (args.output / 'screenshots').mkdir(parents=True, exist_ok=True)
    records = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        tasks = [(repo, view) for repo in repos for view in VIEWPORTS]
        for start in range(0, len(tasks), 4):
            records.extend(await asyncio.gather(*(inspect(browser, repo, view, rules, args.output) for repo, view in tasks[start:start + 4])))
        await browser.close()
    findings = [finding for record in records for finding in evaluate(record, rules)]
    # Comparar tipografía del footer solo como observación; el contenido puede variar.
    for view in VIEWPORTS:
        ref = next((r for r in records if r['repo'] == rules['reference_repo'] and r['viewport'] == view), None)
        ref_body = ref.get('measurements', {}).get('footer_body') if ref else None
        if ref_body:
            for record in records:
                body = record.get('measurements', {}).get('footer_body')
                if body and record['viewport'] == view and body['fontSize'] != ref_body['fontSize']:
                    findings.append({'repo': record['repo'], 'viewport': view, 'rule': 'footer.typography_variant', 'level': 'revision', 'description': 'El primer párrafo del footer usa ' + body['fontSize'] + '; la referencia usa ' + ref_body['fontSize'] + '.', 'evidence': {'observed': body, 'reference': ref_body}})
    result = {'phase': 2, 'status': 'completo' if len(records) == 16 and not any(r.get('error') for r in records) else 'incompleto', 'pages': records, 'findings': findings, 'counts': dict(Counter(f['level'] for f in findings)), 'restrictions': ['Sin sesión ni credenciales', 'Solo GET/HEAD al dominio público CREBE', 'Supabase, servicios externos, sockets y service workers bloqueados', 'Sin clics, formularios o cambios de datos'], 'limits': ['La web publicada puede corresponder a una versión distinta del commit inventariado', 'Solo portadas; contenido dinámico externo incompleto', 'No comprobación funcional ni certificación de accesibilidad']}
    (args.output / 'visual.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    write_report(static, result, args.output)
    print('Auditoría visual:', result['status'], result['counts'])
    return result['status']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, default=Path('reports/inventory'))
    parser.add_argument('--rules', type=Path, default=Path('rules/consistency.json'))
    parser.add_argument('--output', type=Path, default=Path('reports/consistency'))
    args = parser.parse_args()
    status = asyncio.run(run(args))
    raise SystemExit(0 if status == 'completo' else 1)
