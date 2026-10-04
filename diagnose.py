"""Fase 3: causas y propuestas con fuentes Git y experimentos locales en navegador."""
import argparse
import asyncio
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit
from audit import read
from inventory import target_for
from visual_audit import allowed_request, DOM_MEASURE, VIEWPORTS


def share_features(content):
    return {
        'normalizes_label': bool(re.search(r'\.textContent\s*=\s*[\"\x27]Compartir[\"\x27]', content)),
        'native_share': 'navigator.share' in content,
        'channel_menu': 'eva-compartir-menu' in content,
        'copy_fallback': 'navigator.clipboard' in content,
        'share_statistics_reference': 'registrarAccionCompartir' in content,
    }


def source_links(repo, path, commit):
    return 'https://github.com/crebeucayali/' + repo + '/blob/' + commit + '/' + path


async def matched_rules(session, selector, stylesheets, sources, properties):
    root = await session.send('DOM.getDocument')
    node = await session.send('DOM.querySelector', {'nodeId': root['root']['nodeId'], 'selector': selector})
    if not node.get('nodeId'):
        return []
    result = await session.send('CSS.getMatchedStylesForNode', {'nodeId': node['nodeId']})
    evidence = []
    for entry in result.get('matchedCSSRules', []):
        rule = entry['rule']
        props = [p for p in rule['style'].get('cssProperties', []) if p['name'] in properties and not p.get('disabled')]
        if not props:
            continue
        sheet = stylesheets.get(rule.get('styleSheetId'), {})
        url = sheet.get('sourceURL', '')
        target = target_for(url)
        source = sources.get(target)
        evidence.append({'selector': rule.get('selectorList', {}).get('text'), 'stylesheet_url': url, 'repo': target[0] if target else None, 'path': target[1] if target else None, 'line': rule['style'].get('range', {}).get('startLine', -1) + 1, 'properties': [{'name': p['name'], 'value': p['value'], 'important': p.get('important', False)} for p in props], 'source_blob_sha': source['sha'] if source else None, 'media': [{'text': m.get('text'), 'active': [q.get('active') for q in m.get('mediaList', [])]} for m in rule.get('media', [])]})
    return evidence


OVERFLOW_MEASURE = r'''() => {
  const selector = el => {
    if (el.id) return '#' + CSS.escape(el.id);
    const parts = [];
    while (el && el.nodeType === 1 && el.tagName !== 'HTML') {
      const tag = el.tagName.toLowerCase();
      const siblings = [...el.parentElement.children].filter(x => x.tagName === el.tagName);
      parts.unshift(tag + ':nth-of-type(' + (siblings.indexOf(el)+1) + ')');
      el = el.parentElement;
    }
    return parts.join(' > ');
  };
  return [...document.body.querySelectorAll('*')].map(el => {
    const s=getComputedStyle(el),r=el.getBoundingClientRect();
    return {selector:selector(el),className:typeof el.className==='string'?el.className:'',text:el.innerText?.trim().slice(0,110),
      left:r.left,right:r.right,width:r.width,display:s.display,visibility:s.visibility,
      minWidth:s.minWidth,maxWidth:s.maxWidth,whiteSpace:s.whiteSpace,overflowX:s.overflowX,
      fontSize:s.fontSize,flexShrink:s.flexShrink,paddingLeft:s.paddingLeft,paddingRight:s.paddingRight,
      excess:Math.max(r.right-innerWidth,-r.left,0)};
  }).filter(x=>x.width>0&&x.display!=='none'&&x.visibility!=='hidden'&&x.excess>1)
    .sort((a,b)=>b.excess-a.excess).slice(0,30);
}'''

TRIAL = r'''({selector, properties}) => {
  const elements = [...document.querySelectorAll(selector)];
  window.__crebeTrial = elements.map(el=>[el,el.getAttribute('style')]);
  for (const el of elements) for(const [name,value] of Object.entries(properties)) el.style.setProperty(name,value,'important');
}'''
RESTORE = r'''() => {
  for(const [el,style] of window.__crebeTrial||[]) {if(style===null)el.removeAttribute('style');else el.setAttribute('style',style);}
  delete window.__crebeTrial;
}'''


async def browser_case(browser, record, rules, sources, visual_findings):
    result = {'repo': record['repo'], 'viewport': record['viewport'], 'url': record['url'], 'navigation': None, 'overflow': None}
    context = await browser.new_context(viewport=VIEWPORTS[record['viewport']], service_workers='block', accept_downloads=False)
    async def network(route):
        if allowed_request(route.request.url, route.request.method):
            await route.continue_()
        else:
            await route.abort()
    async def socket(route):
        await route.close()
    await context.route('**/*', network)
    await context.route_web_socket('**/*', socket)
    page = await context.new_page()
    session = await context.new_cdp_session(page)
    sheets = {}
    session.on('CSS.styleSheetAdded', lambda event: sheets.update({event['header']['styleSheetId']: event['header']}))
    await session.send('DOM.enable')
    await session.send('CSS.enable')
    try:
        response = await page.goto(record['url'], wait_until='domcontentloaded', timeout=35000)
        if not response or response.status != 200:
            raise RuntimeError('HTTP no verificado')
        await page.wait_for_timeout(1200)
        selectors = record['selectors']
        before = await page.evaluate(DOM_MEASURE, selectors)
        relevant = [f for f in visual_findings if f['repo'] == record['repo'] and f['viewport'] == record['viewport']]
        if any(f['rule'] in {'navigation.font', 'navigation.weight'} for f in relevant):
            evidence = await matched_rules(session, selectors['links'], sheets, sources, {'font', 'font-size', 'font-weight'})
            proposed = {'font-size': str(rules['navigation_font_px'][record['viewport']]) + 'px', 'font-weight': '600'}
            await page.evaluate(TRIAL, {'selector': selectors['links'], 'properties': proposed})
            after = await page.evaluate(DOM_MEASURE, selectors)
            await page.evaluate(RESTORE)
            restored = await page.evaluate(DOM_MEASURE, selectors)
            success = bool(after['nav_links']) and all(link['fontSize'] == proposed['font-size'] and link['fontWeight'] == '600' for link in after['nav_links'])
            result['navigation'] = {'before': before['nav_links'], 'applicable_css_rules': evidence, 'proposal': {'selector': selectors['links'], 'properties': proposed}, 'trial_after': after['nav_links'], 'trial_success': success, 'trial_restored': restored['nav_links'] == before['nav_links'], 'interpretation': 'Reglas aplicables obtenidas de Chromium. La prueba temporal confirma el resultado de la propuesta; no se ha editado el CSS publicado.'}
        if any(f['rule'] == 'layout.overflow' for f in relevant):
            offenders = await page.evaluate(OVERFLOW_MEASURE)
            trials = []
            for offender in offenders[:8]:
                css = await matched_rules(session, offender['selector'], sheets, sources, {'width', 'min-width', 'max-width', 'padding', 'padding-left', 'padding-right', 'margin', 'display', 'grid-template-columns', 'flex', 'flex-shrink', 'white-space', 'overflow-wrap', 'box-sizing'})
                # Cada hipótesis se prueba de forma independiente y después se revierte.
                for properties in [{'min-width': '0', 'max-width': '100%', 'overflow-wrap': 'anywhere'}, {'min-width': '0', 'max-width': '100%', 'box-sizing': 'border-box'}]:
                    await page.evaluate(TRIAL, {'selector': offender['selector'], 'properties': properties})
                    after = await page.evaluate(DOM_MEASURE, selectors)
                    await page.evaluate(RESTORE)
                    restored = await page.evaluate(DOM_MEASURE, selectors)
                    trials.append({'element': offender, 'applicable_css_rules': css, 'properties': properties, 'before_px': before['horizontal_overflow'], 'after_px': after['horizontal_overflow'], 'restored_px': restored['horizontal_overflow'], 'verified': after['horizontal_overflow'] <= 2 and restored['horizontal_overflow'] == before['horizontal_overflow']})
            result['overflow'] = {'before_px': before['horizontal_overflow'], 'offenders': offenders, 'trials': trials, 'verified_candidates': [t for t in trials if t['verified']], 'interpretation': 'Un candidato que elimina el desbordamiento es evidencia experimental, no prueba de que sea el único elemento implicado. Debe validarse en todos los tamaños antes de aplicar.'}
    except Exception as exc:
        result['error'] = type(exc).__name__
    finally:
        await context.close()
    return result


def static_diagnosis(snapshot, static, visual):
    sources = {(s['repo'], s['path']): s for s in snapshot['sources']}
    cases = []
    missing = [f for f in static['findings'] if f['rule'] == 'component.accesibilidad']
    for f in missing:
        source = sources.get((f['repo'], f['path']))
        cases.append({'category': 'accessibility', 'repo': f['repo'], 'path': f['path'], 'status': 'ausencia_estatica_confirmada' if source and 'accesibilidad.js' not in source['content'] else 'requiere_revision', 'cause': 'La página no referencia el helper institucional de accesibilidad.', 'proposal': 'Añadir los enlaces al CSS y JavaScript compartidos de accesibilidad, revisar CSP y comprobar el botón y sus opciones en navegador.', 'evidence': {'source_blob_sha': source['sha'] if source else None, 'script_lines': [i for i, line in enumerate(source['content'].splitlines(), 1) if '<script' in line] if source else []}})
    by_script = defaultdict(list)
    for group in static['shared_script_variants']:
        for ref in group['references']:
            key = (group['script'], ref.get('code_sha256'), ref.get('target_repo'), ref.get('target_path'))
            by_script[key].append(ref)
    for key, refs in by_script.items():
        script, codehash, repo, path = key
        if script != 'compartir-facebook.js':
            continue
        source = sources.get((repo, path))
        if not source:
            continue
        cases.append({'category': 'shared_script', 'repo': repo, 'path': path, 'status': 'variante_identificada', 'code_sha256': codehash, 'source_blob_sha': source['sha'], 'features': share_features(source['content']), 'references': [{'repo': r['repo'], 'path': r['path'], 'cache_query': r['cache_query']} for r in refs], 'proposal': 'Revisar el conjunto de scripts cargados en cada página antes de unificar. Un helper local de etiquetas o estadísticas puede coexistir con el helper central; las huellas distintas no demuestran un defecto.'})
    for repo in sorted({f['repo'] for f in visual['findings'] if f['rule'] == 'share.label'}):
        for (source_repo, path), source in sources.items():
            if source_repo == repo and path.endswith('.html') and 'Compartir en Facebook' in source['content']:
                local = sources.get((repo, 'compartir-facebook.js'))
                features = share_features(local['content']) if local else {}
                cases.append({'category': 'share_label', 'repo': repo, 'path': path, 'status': 'causa_estatica_confirmada' if local and not features.get('normalizes_label') else 'requiere_revision', 'cause': 'El HTML contiene la etiqueta antigua y el helper local no la normaliza a Compartir.', 'evidence': {'html_lines': [i for i, line in enumerate(source['content'].splitlines(), 1) if 'Compartir en Facebook' in line], 'html_blob_sha': source['sha'], 'helper_path': 'compartir-facebook.js', 'helper_blob_sha': local['sha'] if local else None, 'helper_features': features}, 'proposal': 'Actualizar la etiqueta HTML y su aria-label en esta página; añadir normalización de etiqueta al helper local conservando su comportamiento. No sustituir todo el helper sin una revisión funcional.', 'functional_diagnosis': 'No se pulsó Compartir ni se comprobó el destino.'})
    return cases


def report(result, output):
    lines = ['# Diagnóstico CREBE, fase 3', '', 'Estado: ' + result['status'] + '. Inventario: ' + result['inventory_captured_at'] + '.', '', 'Las pruebas cambian estilos únicamente en un navegador aislado y luego los restauran. No se modificaron los ocho repositorios, bases de datos o configuraciones.', '', '## Desbordamiento móvil', '']
    for case in result['browser_cases']:
        if not case.get('overflow'):
            continue
        overflow = case['overflow']
        lines.append(case['repo'] + ': ' + str(overflow['before_px']) + ' px de desbordamiento inicial.')
        for candidate in overflow['verified_candidates']:
            element = candidate['element']
            locations = sorted({(r.get('repo') or '?') + '/' + (r.get('path') or '?') + ':' + str(r['line']) for r in candidate['applicable_css_rules']})
            lines.extend(['', '- Elemento: `' + element['selector'] + '`, clases `' + element['className'] + '`.', '- Reglas aplicables: ' + ', '.join(locations) + '.', '- Propuesta temporal: `' + json.dumps(candidate['properties'], ensure_ascii=False) + '`.', '- Resultado: ' + str(candidate['after_px']) + ' px. Al revertir: ' + str(candidate['restored_px']) + ' px.'])
        if not overflow['verified_candidates']:
            lines.append('No se confirmó una corrección con las hipótesis ensayadas. Revisar los elementos y sus reglas registrados en diagnosis.json.')
    lines.extend(['', '## Tipografía de navegación', '', '| Repositorio | Vista | Antes | Propuesta | Prueba y restauración |', '|---|---|---|---|---|'])
    for case in result['browser_cases']:
        n = case.get('navigation')
        if n:
            before = ', '.join(sorted({x['fontSize'] + '/' + x['fontWeight'] for x in n['before']}))
            locations = ', '.join(sorted({(r.get('path') or '?') + ':' + str(r['line']) for r in n['applicable_css_rules']}))
            lines.append('| ' + case['repo'] + ' (' + locations + ') | ' + case['viewport'] + ' | ' + before + ' | ' + json.dumps(n['proposal']['properties']) + ' | ' + str(n['trial_success'] and n['trial_restored']) + ' |')
    lines.extend(['', 'Las reglas CSS aplicables, sus archivos, líneas y propiedades !important están en diagnosis.json. Las correcciones propuestas deben hacerse en esas declaraciones, con selectores limitados a la navegación institucional. No se propone cambiar la tipografía de toda la página.', '', '## Compartir y accesibilidad', ''])
    for case in result['static_cases']:
        if case['category'] == 'shared_script':
            continue
        lines.extend(['- ' + case['repo'] + '/' + case['path'] + ': ' + case['cause'] + ' Estado: ' + case['status'] + '.', '  Propuesta: ' + case['proposal']])
    lines.extend(['', '## Variantes de scripts', '', '| Archivo | Etiqueta normalizada | API nativa | Menú multicanal | Referencia estadística |', '|---|---|---|---|---|'])
    for case in result['static_cases']:
        if case['category'] == 'shared_script':
            f = case['features']
            lines.append('| ' + case['repo'] + '/' + case['path'] + ' | ' + ' | '.join(str(f[k]) for k in ['normalizes_label', 'native_share', 'channel_menu', 'share_statistics_reference']) + ' |')
    lines.extend(['', 'Son características detectadas en el código, no funciones probadas. Las variantes no se reemplazan automáticamente. Las referencias repetidas del inventario se agrupan por archivo y huella.', '', '## Siguiente intervención propuesta', '', 'Primero confirmar la corrección del desbordamiento a varios anchos. Después tratar las declaraciones CSS de navegación, la etiqueta de Compartir en DUA y el helper de accesibilidad ausente. Cada intervención debe limitarse al repositorio y los archivos indicados, con pruebas y un cambio independiente.', '', 'Esta fase no crea ramas ni pull requests en EVA. La consistencia funcional completa, MFA, datos y acciones de usuario permanecen fuera del diagnóstico.', ''])
    (output / 'Informe_fase_3.md').write_text('\n'.join(lines), encoding='utf-8')


async def main(args):
    from playwright.async_api import async_playwright
    snapshot = read(args.snapshot)
    static = read(args.consistency / 'consistency.json')
    visual = read(args.consistency / 'visual.json')
    rules = read(args.rules)
    sources = {(s['repo'], s['path']): s for s in snapshot['sources']}
    affected = {(f['repo'], f['viewport']) for f in visual['findings'] if f['rule'] in {'navigation.font', 'navigation.weight', 'layout.overflow'}}
    records = [r for r in visual['pages'] if (r['repo'], r['viewport']) in affected]
    cases = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for start in range(0, len(records), 4):
            cases.extend(await asyncio.gather(*(browser_case(browser, r, rules, sources, visual['findings']) for r in records[start:start+4])))
        await browser.close()
    result = {'phase': 3, 'status': 'completo' if static['audit_status'] == 'completo' and visual['status'] == 'completo' and not any(c.get('error') for c in cases) else 'incompleto', 'inventory_captured_at': snapshot['captured_at'], 'browser_cases': cases, 'static_cases': static_diagnosis(snapshot, static, visual), 'limits': ['Estilos modificados y restaurados solo en memoria del navegador de diagnóstico', 'No prueba de acciones, autenticación, datos o Supabase', 'Una corrección temporal exitosa es una hipótesis comprobada en ese viewport, no una validación de todos los tamaños', 'La web publicada puede diferir del commit de fuente', 'Las reglas CDP son aplicables; no se atribuye un ganador de cascada sin evidencia adicional']}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'diagnosis.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    report(result, args.output)
    print('Diagnóstico:', result['status'], 'casos en navegador:', len(cases))
    return result['status']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--consistency', type=Path, default=Path('reports/consistency'))
    parser.add_argument('--rules', type=Path, default=Path('rules/consistency.json'))
    parser.add_argument('--output', type=Path, default=Path('reports/diagnosis'))
    args = parser.parse_args()
    raise SystemExit(0 if asyncio.run(main(args)) == 'completo' else 1)
