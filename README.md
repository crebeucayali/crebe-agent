# CREBE Agent, fase 1

Inventario estático de los ocho repositorios de CREBE Ucayali. Python 3.10 o superior, sin dependencias adicionales.

Ejecutar desde esta carpeta:

```bash
python inventory.py --output inventory
```

En Windows también puede utilizarse `py inventory.py --output inventory`.

El programa utiliza únicamente solicitudes GET a la API de GitHub. Lee la rama predeterminada y fija los archivos a sus huellas Git antes de analizarlos. No clona, modifica, ejecuta ni publica código de los repositorios. Tampoco consulta Supabase o carga las páginas, lo que evita incrementar los contadores durante el inventario.

La API pública puede agotar su límite antes de completar las aproximadamente 217 lecturas. Para ejecuciones futuras se puede proporcionar `GITHUB_TOKEN` en el entorno, con permisos únicamente de lectura de contenido. No guardar tokens en archivos del proyecto. Los errores se registran por tipo, sin imprimir credenciales.

El inventario incluido fue obtenido el 4 de octubre de 2026 mediante el acceso conectado a GitHub. Las bibliotecas de terceros y los archivos binarios figuran en el listado de archivos, pero su contenido no se analiza. Los enlaces externos se registran y no se visitan.

Archivos generados:

- `repositories.json`: repositorios, commits, ramas, configuración Pages y listado de archivos.
- `components.json`: evidencia por página y declaraciones CSS institucionales.
- `technologies.json`: referencias a tecnologías, con archivos y líneas.
- `dependencies.json`: scripts y estilos, URLs resueltas, parámetros de caché y huellas.
- `manifest.json`: cobertura, fecha, método, límites y fallos.
- `Informe_fase_1.md`: informe legible.

Los componentes se detectan mediante marcadores estáticos. Una coincidencia no prueba que funcionen; una ausencia no determina una inconsistencia. Pueden existir componentes generados dinámicamente. Las páginas auxiliares y administrativas requieren reglas diferentes de las portadas.

Las declaraciones CSS se guardan como evidencia, sin calcular la cascada ni el resultado visual. No se adoptan automáticamente como estándar. Las versiones `?v=` son identificadores de caché; se conservan también las huellas del código para comparaciones posteriores.

Ejecutar las comprobaciones:

```bash
python -m unittest discover -s tests
```

## Ejecutar en GitHub Actions

Abrir Actions, seleccionar "Inventario CREBE - Fase 1" y pulsar "Run workflow" sobre la rama main. Al terminar, el resumen muestra el informe y la sección Artifacts permite descargar el inventario completo.

La primera ejecución se inicia al incorporar la configuración. También se verifica cuando cambia únicamente el archivo del workflow. No hay ejecución periódica ni activación por cambios en los ocho repositorios de EVA.

El workflow utiliza el token temporal de GitHub con contents: read. No guarda credenciales, realiza commits, cambia páginas ni consulta Supabase. Cada ejecución lee los ocho repositorios públicos y conserva sus resultados como artefactos durante 30 días. El inventario inicial en inventory/ permanece como referencia histórica; los informes nuevos se generan en reports/inventory/ dentro de la ejecución.

El siguiente paso es definir reglas de consistencia por tipo de página y contrastarlas con el resultado visual.


## Fase 2: auditoría de consistencia

El workflow "Consistencia CREBE - Fase 2" genera un inventario nuevo, ejecuta las reglas estáticas y mide las ocho portadas en Chromium a 1440 × 900 y 390 × 844 px. Las páginas auxiliares y administrativas tienen reglas distintas. No se igualan contenidos, colores ni módulos.

Abrir Actions, seleccionar "Consistencia CREBE - Fase 2" y pulsar "Run workflow". También se verifica al cambiar sus reglas, programa, pruebas o configuración. Los cambios en los ocho repositorios de EVA no lo activan automáticamente.

Los artefactos contienen el inventario, `consistency/Informe_fase_2.md`, `consistency/consistency.json`, `consistency/visual.json` y 16 capturas de pantalla. Los resultados nuevos se conservan 30 días. Un workflow exitoso indica que terminó la auditoría; el informe puede contener inconsistencias.

Reglas en `rules/consistency.json`: tipografía NAV 15 px en escritorio / 14 px en móvil, franja de peso 500–700, referencia de 74 px para la navegación, etiqueta Compartir, componentes comunes y exclusiones por tipo de página. La altura total del hero no se compara con 74 px. Las variaciones del footer y de código compartido requieren revisión contextual.

La revisión visual usa contextos nuevos sin sesión. Solo permite GET/HEAD a crebeucayali.github.io y bloquea servicios externos, Supabase, sockets y service workers. No pulsa Compartir, inicia sesión, rellena formularios ni prueba cargas. El contenido dependiente del backend puede estar incompleto. La versión publicada puede diferir del commit inventariado. Se revisan portadas visualmente y todos los HTML de forma estática; no es una certificación de accesibilidad.

Ejecución local:

```bash
python audit.py --inventory inventory --output reports/consistency
python -m pip install -r requirements-audit.txt
python -m playwright install chromium
python visual_audit.py --inventory inventory --output reports/consistency
```

La fase 2 solo informa. No modifica los ocho repositorios ni genera correcciones, commits o PR en ellos.
