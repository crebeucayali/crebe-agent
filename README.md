# CREBE Agent

Agente de auditoría, monitoreo y mantenimiento controlado de EVA para los ocho repositorios de CREBE Ucayali. El estado operativo actual mantiene los monitores de Funcionamiento (Fase 5), Integridad (Fase 6), Seguridad (Fase 7) y Accesibilidad (Fase 8), el estado canónico y el mantenimiento del Directorio de Entidades; el Mapa Web está actualizado a su Etapa 6.

Las secciones siguientes conservan la documentación de las herramientas históricas de las Fases 1–3 para ejecuciones controladas.

## Fase 1: inventario histórico

Python 3.10 o superior, sin dependencias adicionales.

Para ejecutar el inventario desde esta carpeta:

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

## Inventario histórico y ejecución controlada

El workflow histórico "Inventario CREBE - Fase 1" fue retirado de `.github/workflows/` una vez concluida la etapa de construcción inicial del agente. `inventory.py`, sus pruebas y el inventario histórico se conservan para ejecuciones controladas cuando sea necesario actualizar o reproducir la evidencia.

No hay ejecución periódica ni activación automática por cambios en los ocho repositorios de EVA. Una ejecución nueva del inventario debe iniciarse de forma deliberada mediante el comando local indicado arriba o desde un entorno controlado con permisos de solo lectura.

El programa puede utilizar un token temporal de GitHub con `contents: read`. No guarda credenciales, realiza commits, cambia páginas ni consulta Supabase. El inventario inicial en `inventory/` permanece como referencia histórica; los informes nuevos pueden generarse en `reports/inventory/`.

El siguiente paso es definir reglas de consistencia por tipo de página y contrastarlas con el resultado visual.


## Fase 2: auditoría de consistencia

Las herramientas de la Fase 2 generan un inventario nuevo, ejecutan las reglas estáticas y pueden medir las ocho portadas en Chromium a 1440 × 900 y 390 × 844 px. Las páginas auxiliares y administrativas tienen reglas distintas. No se igualan contenidos, colores ni módulos.

El workflow histórico "Consistencia CREBE - Fase 2" fue retirado de `.github/workflows/`. Se conservan `audit.py`, `visual_audit.py`, `rules/`, las pruebas y las dependencias necesarias para ejecutar esta auditoría de forma controlada cuando corresponda. Los cambios en los ocho repositorios de EVA no disparan automáticamente esta auditoría.

Los resultados pueden contener el inventario, `consistency/Informe_fase_2.md`, `consistency/consistency.json`, `consistency/visual.json` y 16 capturas de pantalla. Una ejecución correcta indica que terminó la auditoría; el informe puede contener inconsistencias.

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


## Fase 3: diagnóstico de hallazgos

El workflow histórico "Diagnostico CREBE - Fase 3" fue retirado de `.github/workflows/`. Se conserva `diagnose.py` y la lógica asociada para diagnósticos controlados cuando exista una necesidad concreta. No hay ejecución periódica ni acciones automáticas sobre EVA.

La ejecución controlada actualiza el inventario, repite la auditoría de consistencia y contrasta los hallazgos con fuentes Git y reglas CSS aplicables obtenidas desde Chromium. Prueba hipótesis con estilos temporales únicamente en un contexto de navegador aislado y restaura cada ensayo. No publica esas modificaciones.

Los resultados se guardan en `diagnosis/Informe_fase_3.md` y `diagnosis/diagnosis.json`, junto al inventario, auditoría y capturas. Incluyen elementos que sobresalen del viewport, reglas CSS con archivo/línea/huella, medidas antes/después/restauradas, causas de etiquetas y accesibilidad, y características de las variantes de Compartir.

Un ensayo exitoso confirma la propuesta en el viewport probado. No acredita que sea la única solución ni valida todos los tamaños. Las reglas CDP son reglas aplicables; no se presupone que la última regla registrada sea la ganadora de la cascada. Los casos no comprobados permanecen como hipótesis.

La captura de fuentes públicas se guarda temporalmente fuera de los artefactos. El token no se guarda. No se modifican datos, sesiones, MFA, permisos ni los ocho repositorios, y no se crean ramas o PR en ellos.

Ejecución local, después de preparar Chromium:

```bash
python inventory.py --output reports/inventory --save-snapshot /tmp/crebe-source-snapshot.json
python audit.py --inventory reports/inventory --output reports/consistency
python visual_audit.py --inventory reports/inventory --output reports/consistency
python diagnose.py --snapshot /tmp/crebe-source-snapshot.json --consistency reports/consistency --output reports/diagnosis
```
