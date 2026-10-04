"""Fase 2: reglas explícitas y evidencia estática, sin modificar repositorios."""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def page_kind(page, rules):
    path = page['path']
    if re.search(r'(^|/)(admin(?:[./-]|$)|panel(?:[./-]|$))', path, re.I) or page.get('scope') == 'administrativo':
        return 'administrativa'
    if path in rules.get('auxiliary_pages', {}).get(page['repo'], []):
        return 'auxiliar'
    if any(re.search(pattern, path, re.I) for pattern in rules['auxiliary_path_patterns']):
        return 'auxiliar'
    if any(re.search(pattern, page.get('title', ''), re.I) for pattern in rules['auxiliary_title_patterns']):
        return 'auxiliar'
    return 'portada' if path == 'index.html' else 'publica'


def audit(inventory, rules, output):
    manifest = read(inventory / 'manifest.json')
    components = read(inventory / 'components.json')
    repositories = read(inventory / 'repositories.json')
    files = {r['repo']: {f['path'] for f in r['files']} for r in repositories}
    commits = {r['repo']: r['commit'] for r in repositories}
    findings = []
    coverage = []
    scripts = defaultdict(list)

    def finding(page, rule, level, description, evidence):
        findings.append({'repo': page['repo'], 'path': page['path'], 'rule': rule, 'level': level, 'description': description, 'evidence': evidence, 'source_url': 'https://github.com/crebeucayali/' + page['repo'] + '/blob/' + commits[page['repo']] + '/' + page['path']})

    for p in components['pages']:
        kind = page_kind(p, rules)
        coverage.append({'repo': p['repo'], 'path': p['path'], 'kind': kind})
        required = rules['home_required_components'] if kind == 'portada' else rules['public_required_components'] if kind == 'publica' else []
        for key in required:
            if not p['components'].get(key):
                finding(p, 'component.' + key, 'revision', 'No se encontró evidencia estática de ' + key + ' en una página ' + kind + '.', {'expected': key, 'observed': 'sin marcador; comprobar generación dinámica'})
        if kind in {'publica', 'portada'}:
            for image in p['images']:
                if not image['alt_present']:
                    finding(p, 'image.alt', 'inconsistencia', 'Una imagen carece del atributo alt.', image)
        for dep in p['references']:
            target_repo, target_path = dep.get('target_repo'), dep.get('target_path')
            if target_repo and target_path and target_path not in files.get(target_repo, set()):
                finding(p, 'reference.exists', 'inconsistencia', 'El script o estilo apunta a un archivo ausente del inventario.', {'line': dep['line'], 'url': dep['resolved_url'], 'target_repo': target_repo, 'target_path': target_path})
            if dep['kind'] == 'script' and Path(urlsplit(dep['resolved_url']).path).name in rules['shared_scripts']:
                scripts[Path(urlsplit(dep['resolved_url']).path).name].append({'repo': p['repo'], 'path': p['path'], 'url': dep['resolved_url'], 'cache_query': dep['query'], 'code_sha256': dep.get('target_content_sha256'), 'target_repo': target_repo, 'target_path': target_path})
    variants = []
    for name, refs in sorted(scripts.items()):
        hashes = sorted({r['code_sha256'] for r in refs if r['code_sha256']})
        versions = sorted({r['cache_query'] for r in refs})
        variants.append({'script': name, 'code_variants': len(hashes), 'cache_queries': versions, 'code_hashes': hashes, 'references': refs, 'interpretation': 'Diferencias registradas; validar compatibilidad e intención antes de corregir.'})
        if len(hashes) > 1:
            for ref in refs:
                finding(ref, 'shared.code_variant', 'revision', name + ' tiene varias huellas de código en el ecosistema.', {'code_sha256': ref['code_sha256'], 'variants': len(hashes), 'url': ref['url']})
    result = {'phase': 2, 'audit_status': 'completo' if manifest['status'] == 'completo' else 'incompleto', 'inventory_captured_at': manifest['captured_at'], 'reference_repo': rules['reference_repo'], 'coverage': coverage, 'findings': findings, 'counts': dict(Counter(f['level'] for f in findings)), 'shared_script_variants': variants, 'limits': rules['limits'], 'interpretation': 'Ejecución correcta no equivale a ausencia de inconsistencias. Revisión significa que falta verificar el contexto.'}
    output.mkdir(parents=True, exist_ok=True)
    (output / 'consistency.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    write_report(result, None, output)
    return result


def write_report(static, visual, output):
    lines = ['# Auditoría de consistencia CREBE, fase 2', '', 'Inventario: ' + static['inventory_captured_at'], '', 'Estado del análisis estático: ' + static['audit_status'] + '.', '', 'Cobertura: ' + str(len(static['coverage'])) + ' archivos HTML. Las páginas administrativas, auxiliares y públicas se evalúan con reglas diferentes.', '', '## Scripts comunes', '', '| Script | Variantes de código | Parámetros de caché |', '|---|---:|---|']
    for group in static['shared_script_variants']:
        lines.append('| ' + group['script'] + ' | ' + str(group['code_variants']) + ' | ' + ', '.join(group['cache_queries']) + ' |')
    lines.extend(['', 'Una diferencia de versión de caché no demuestra una diferencia de código. Varias huellas de código requieren revisar compatibilidad y propósito.', '', '## Hallazgos estáticos', '', '| Repositorio y archivo | Nivel | Regla | Observación |', '|---|---|---|---|'])
    for f in static['findings']:
        lines.append('| [' + f['repo'] + '/' + f['path'] + '](' + f['source_url'] + ') | ' + f['level'] + ' | ' + f['rule'] + ' | ' + f['description'].replace('|', '/') + ' |')
    if not static['findings']:
        lines.append('| Todos los archivos evaluados | sin hallazgos | reglas estáticas | No se detectaron diferencias según estas reglas. |')
    lines.extend(['', 'Las evidencias y líneas concretas están en consistency.json.', '', '## Comprobación visual', ''])
    if visual is None:
        lines.append('Pendiente. Este informe por sí solo no acredita consistencia visual.')
    else:
        lines.extend(['Estado: ' + visual['status'] + '. Se miden las ocho portadas en escritorio y móvil. Los subaccesos tienen análisis estático.', '', '| Repositorio | Vista | HTTP | Navegación, alto / mínimo CSS | Tamaños de enlaces | Desbordamiento |', '|---|---|---|---|---|---|'])
        for v in visual['pages']:
            measure = v.get('measurements', {})
            nav = measure.get('nav') or {}
            fonts = sorted({x['fontSize'] for x in measure.get('nav_links', [])})
            lines.append('| ' + v['repo'] + ' | ' + v['viewport'] + ' | ' + str(v.get('http_status', 'no comprobado')) + ' | ' + str(nav.get('height', '-')) + ' / ' + str(nav.get('minHeight', '-')) + ' | ' + ', '.join(fonts) + ' | ' + str(measure.get('horizontal_overflow', '-')) + ' |')
        lines.extend(['', '| Repositorio | Vista | Nivel | Observación |', '|---|---|---|---|'])
        for f in visual['findings']:
            lines.append('| ' + f['repo'] + ' | ' + f['viewport'] + ' | ' + f['level'] + ' | ' + f['description'].replace('|', '/') + ' |')
        lines.extend(['', 'Los detalles de cada medición, bloqueos y errores están en visual.json. Las capturas permiten revisar el contexto. Los servicios externos, Supabase y las solicitudes de escritura se bloquean; los contenidos dinámicos pueden estar incompletos. No se prueban interacciones ni autenticación.'])
    lines.extend(['', '## Alcance', '', 'La altura de referencia de 74 px se compara con la franja de navegación en escritorio, no con la portada completa ni con una cabecera móvil que se distribuye en varias líneas. Footer, navegación y enlaces se registran sin imponer idéntico contenido a módulos distintos.', '', 'La etiqueta visible de Compartir, tamaños de navegación, pesos tipográficos y desbordamiento se comprueban en navegador. Las reglas de 15 px en escritorio y 14 px en móvil proceden del criterio acordado para EVA. Las diferencias del footer frente a la referencia se registran para revisión; no son errores por sí solas.', '', 'No se modifican páginas, datos, permisos, contadores o MFA. No es una certificación de accesibilidad ni una comprobación del funcionamiento de los servicios.', ''])
    (output / 'Informe_fase_2.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, default=Path('inventory'))
    parser.add_argument('--rules', type=Path, default=Path('rules/consistency.json'))
    parser.add_argument('--output', type=Path, default=Path('reports/consistency'))
    args = parser.parse_args()
    result = audit(args.inventory, read(args.rules), args.output)
    print('Auditoría estática:', result['audit_status'], result['counts'])
    raise SystemExit(0 if result['audit_status'] == 'completo' else 1)
