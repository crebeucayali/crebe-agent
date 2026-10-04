"""Inventario CREBE: solo GET a GitHub; no ejecuta código de los repositorios."""
import argparse
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
from urllib.request import Request, urlopen

OWNER = 'crebeucayali'
REPOS = ['crebeucayali.github.io', 'accesos-complementarios', 'capacitaciones',
         'banco-digital-accesible', 'materiales-educativos-accesibles',
         'noti-inclusivos', 'repositorio-accesible', 'DUA-3.0']
RULES = {
    'header': r'<header\b', 'footer': r'<footer\b', 'navegacion': r'<nav\b',
    'compartir': r'data-compartir|compartir-facebook|compartir-eva',
    'contador_visitas': r'data-eva-contador|visitas-eva\.js',
    'accesibilidad': r'accesibilidad\.js',
    'acceso_administrativo': r'admin-toggle|admin-acceso\.js|admin-mini-form',
    'privacidad': r'politica-privacidad\.html',
    'cookies': r'politica-cookies\.html',
}

def base_url(repo):
    return 'https://crebeucayali.github.io/' + ('' if repo == REPOS[0] else repo + '/')

def source_entry(entry):
    return entry['type'] == 'blob' and Path(entry['path']).suffix.lower() in {'.html', '.js', '.css'} and not re.search(r'(^|/)(vendor|node_modules)/', entry['path'])

def github_get(path):
    headers = {'User-Agent': 'CREBE-Inventory-ReadOnly', 'Accept': 'application/vnd.github+json'}
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    with urlopen(Request('https://api.github.com/repos/' + OWNER + '/' + path, headers=headers, method='GET'), timeout=40) as response:
        return json.load(response)

def collect():
    import base64
    result = {'captured_at': datetime.now(timezone.utc).isoformat(), 'repositories': [], 'sources': [], 'failures': []}
    for name in REPOS:
        try:
            metadata = github_get(name)
            branch = github_get(name + '/branches/' + metadata['default_branch'])
            commit = branch['commit']['sha']
            tree = github_get(name + '/git/trees/' + commit + '?recursive=1')
            if tree.get('truncated'):
                raise RuntimeError('Árbol truncado: inventario incompleto')
            result['repositories'].append({'name': name, 'repository_full_name': OWNER + '/' + name, 'metadata': {'repository': metadata, 'branch': branch}, 'tree': tree})
            for entry in filter(source_entry, tree['tree']):
                try:
                    blob = github_get(name + '/git/blobs/' + entry['sha'])
                    content = base64.b64decode(blob['content']).decode('utf-8')
                    result['sources'].append(dict(entry, repo=name, full=OWNER + '/' + name, content=content))
                except Exception as exc:
                    result['failures'].append({'repo': name, 'path': entry['path'], 'error_type': type(exc).__name__})
        except Exception as exc:
            result['failures'].append({'repo': name, 'error_type': type(exc).__name__})
    return result

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.elements = []
        self.links = []
        self.images = []
        self._anchor = None
        self._ignored = 0
        self.title = ''
        self._title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in {'script', 'style'}:
            self._ignored += 1
        if tag == 'title':
            self._title = True
        if tag in {'header', 'footer', 'nav'}:
            self.elements.append({'tag': tag, 'class': a.get('class', ''), 'id': a.get('id', ''), 'line': self.getpos()[0]})
        if tag == 'script' and a.get('src'):
            self.refs.append({'kind': 'script', 'value': a['src'], 'line': self.getpos()[0]})
        if tag == 'link' and 'stylesheet' in a.get('rel', '') and a.get('href'):
            self.refs.append({'kind': 'stylesheet', 'value': a['href'], 'line': self.getpos()[0]})
        if tag == 'a':
            self._anchor = {'href': a.get('href', ''), 'text': '', 'line': self.getpos()[0]}
            self.links.append(self._anchor)
        if tag == 'img':
            self.images.append({'alt_present': 'alt' in a, 'decorative': a.get('alt') == '', 'line': self.getpos()[0]})

    def handle_endtag(self, tag):
        if tag in {'script', 'style'}:
            self._ignored = max(0, self._ignored - 1)
        if tag == 'title':
            self._title = False
        if tag == 'a':
            self._anchor = None

    def handle_data(self, data):
        if self._title:
            self.title += data
        if self._anchor and not self._ignored:
            self._anchor['text'] += data

def target_for(url):
    parsed = urlsplit(url)
    if parsed.netloc != 'crebeucayali.github.io':
        return None
    parts = unquote(parsed.path).lstrip('/').split('/')
    repo = parts.pop(0) if parts and parts[0] in REPOS[1:] else REPOS[0]
    path = '/'.join(parts)
    if not path or path.endswith('/'):
        path += 'index.html'
    return repo, path

def build(snapshot, output):
    output.mkdir(parents=True, exist_ok=True)
    sources = {(f['repo'], f['path']): f for f in snapshot['sources']}
    pages, dependencies, css, technologies, repositories = [], [], [], [], []
    for r in snapshot['repositories']:
        name = r['name']
        own = [f for f in snapshot['sources'] if f['repo'] == name]
        files = [e for e in r['tree']['tree'] if e['type'] == 'blob']
        md = r['metadata']['repository']
        commit = r['metadata']['branch']['commit']['sha']
        repositories.append({'repo': name, 'url': 'https://github.com/' + OWNER + '/' + name, 'branch': md.get('default_branch', 'main'), 'commit': commit, 'git_tree_sha': r['metadata']['branch']['commit']['commit']['tree']['sha'], 'archived': md['archived'], 'pages_enabled': md['has_pages'], 'pages_url_expected': base_url(name), 'pages_http_verified': False, 'last_push': md['pushed_at'], 'total_files': len(files), 'extensions': dict(Counter(Path(e['path']).suffix.lower() or '(sin extension)' for e in files)), 'source_files_expected': sum(source_entry(e) for e in files), 'source_files_read': len(own), 'html_files': sum(f['path'].endswith('.html') for f in own), 'files': [{'path': e['path'], 'sha': e['sha'], 'size': e.get('size')} for e in files]})
        tech = {'repo': name, 'evidence': {}}
        for technology, pattern in {'Supabase_reference': r'supabase', 'localStorage': r'\blocalStorage\b', 'sessionStorage': r'\bsessionStorage\b', 'media_queries': r'@media\b', 'Web_Share_API': r'navigator\.share', 'YouTube_reference': r'youtube(?:-nocookie)?\.com|youtu\.be', 'Google_Drive_reference': r'drive\.google\.com'}.items():
            tech['evidence'][technology] = [{'path': f['path'], 'lines': [i for i, line in enumerate(f['content'].splitlines(), 1) if re.search(pattern, line, re.I)]} for f in own if re.search(pattern, f['content'], re.I)]
        technologies.append(tech)
        for f in own:
            if f['path'].endswith('.css'):
                selectors = []
                for match in re.finditer(r'([^{}]+)\{([^{}]*)\}', f['content']):
                    if re.search(r'cabecera|pestanas|pie-crebe|crebe-header|crebe-footer|admin-toggle', match[1]):
                        selectors.append({'selector': match[1].strip(), 'declarations': match[2].strip(), 'line': f['content'][:match.start()].count('\n') + 1})
                css.append({'repo': name, 'path': f['path'], 'sha': f['sha'], 'institutional_rules_declared': selectors, 'note': 'Declaraciones CSS; no medidas renderizadas ni resolución de cascada.'})
            if not f['path'].endswith('.html'):
                continue
            parser = Page()
            parser.feed(f['content'])
            # No considerar comentarios HTML como componentes presentes.
            text = re.sub(r'<!--[\s\S]*?-->', lambda m: '\n' * m.group(0).count('\n'), f['content'])
            evidence = {key: [{'line': i, 'marker': m.group(0)} for i, line in enumerate(text.splitlines(), 1) if (m := re.search(pattern, line, re.I))] for key, pattern in RULES.items()}
            record = {'repo': name, 'path': f['path'], 'sha': f['sha'], 'title': parser.title.strip(), 'url_expected': urljoin(base_url(name), f['path']), 'components': evidence, 'elements': parser.elements, 'references': [], 'links': parser.links, 'images': parser.images, 'scope': 'administrativo' if re.search(r'(^|/)admin', f['path']) else 'pagina_publica_o_auxiliar'}
            for ref in parser.refs:
                absolute = urljoin(record['url_expected'], ref['value'])
                target = target_for(absolute)
                source = sources.get(target) if target else None
                dependency = dict(ref, source_repo=name, source_path=f['path'], resolved_url=absolute, target_repo=target[0] if target else None, target_path=target[1] if target else None, query=urlsplit(absolute).query, target_blob_sha=source['sha'] if source else None, target_content_sha256=hashlib.sha256(source['content'].encode()).hexdigest() if source else None, status='leido' if source else 'externo_o_no_leido')
                record['references'].append(dependency)
                dependencies.append(dependency)
            pages.append(record)
    components = {'classification_proposed': {'common': list(RULES), 'particular': ['galeria', 'calendario', 'banco', 'materiales', 'actividades', 'contenido_principal'], 'note': 'Clasificación inicial. La presencia no obliga a incluir cada componente en todas las páginas.'}, 'pages': pages, 'css_observations': css}
    status = 'completo' if not snapshot['failures'] and len(repositories) == 8 and all(r['source_files_read'] == r['source_files_expected'] for r in repositories) else 'incompleto'
    manifest = {'phase': 1, 'status': status, 'captured_at': snapshot['captured_at'], 'mode': 'read_only', 'method': 'GitHub metadata, recursive trees and pinned blobs; static HTML/CSS/JS analysis', 'excluded_content_scan': ['vendor/', 'node_modules/', 'binary files', 'documentation', 'database records'], 'limits': ['No verificación HTTP de GitHub Pages', 'No ejecución JavaScript ni pruebas de funcionamiento', 'No consulta de Supabase', 'Sin valoración de conformidad visual o accesibilidad'], 'failures': snapshot['failures']}
    for filename, data in [('repositories.json', repositories), ('components.json', components), ('technologies.json', technologies), ('dependencies.json', dependencies), ('manifest.json', manifest)]:
        (output / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    rows = []
    for r in repositories:
        subset = [p for p in pages if p['repo'] == r['repo']]
        counts = [str(sum(bool(p['components'][k]) for p in subset)) for k in ['header', 'footer', 'compartir', 'contador_visitas', 'accesibilidad']]
        rows.append('| ' + ' | '.join([r['repo'], str(r['html_files'])] + counts) + ' |')
    report = '# Inventario CREBE Ucayali, fase 1\n\nFecha: ' + snapshot['captured_at'] + '\n\nEstado: ' + status + '. Ocho repositorios, ' + str(len(pages)) + ' archivos HTML y ' + str(len(sources)) + ' archivos HTML/CSS/JS leídos. Los ocho tienen GitHub Pages habilitado según los metadatos; no se comprobó su respuesta pública.\n\nLos números de la tabla indican archivos HTML con evidencia estática del componente, incluidos accesos administrativos y páginas auxiliares. No constituyen una evaluación de funcionamiento ni una lista de componentes obligatorios.\n\n| Repositorio | HTML | Header | Footer | Compartir | Visitas | Accesibilidad |\n|---|---:|---:|---:|---:|---:|---:|\n' + '\n'.join(rows) + '\n\nCada página está registrada con ruta, huella Git, título, componentes, scripts, estilos y enlaces. Las dependencias conservan la URL y su parámetro de caché, así como la huella del archivo cuando se pudo leer. Una versión de caché diferente no demuestra por sí sola un código diferente.\n\nLas reglas CSS institucionales se registran como declaraciones. Las alturas y tamaños efectivos se deberán medir en navegador durante la fase 2. La plataforma principal queda como referencia candidata; sus valores actuales todavía no se aprueban como estándar.\n\nLas referencias a Supabase y almacenamiento del navegador se identificaron en el código. No se accedió a datos, sesiones o permisos. No se modificaron los repositorios ni se realizaron commits, despliegues o cambios de configuración.\n\nLa clasificación inicial separa componentes institucionales de módulos y contenidos particulares. Debe revisarse qué componentes corresponden a cada tipo de página antes de interpretar ausencias como errores.\n\nEl programa incluido permite actualizar el inventario mediante solicitudes GET. No se instaló una tarea programada ni se creó un repositorio remoto para el agente.\n'
    (output / 'Informe_fase_1.md').write_text(report, encoding='utf-8')
    return status

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, help='Reprocesar captura local sin red')
    parser.add_argument('--output', type=Path, default=Path('inventory'))
    parser.add_argument('--save-snapshot', type=Path, help='Guardar fuentes públicas para diagnóstico local; no contiene el token')
    args = parser.parse_args()
    snapshot = json.loads(args.snapshot.read_text(encoding='utf-8')) if args.snapshot else collect()
    if args.save_snapshot:
        args.save_snapshot.write_text(json.dumps(snapshot, ensure_ascii=False), encoding='utf-8')
    status = build(snapshot, args.output)
    print('Inventario ' + status + ': ' + str(args.output.resolve()))
    raise SystemExit(0 if status == 'completo' else 1)

if __name__ == '__main__':
    main()
