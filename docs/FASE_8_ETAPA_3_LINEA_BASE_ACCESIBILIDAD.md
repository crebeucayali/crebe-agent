# Fase 8 — Etapa 3: Línea base de accesibilidad

## Estado

`ETAPA_3_COMPLETADA_LINEA_BASE_ACCESIBILIDAD`

Fecha: 2026-10-08  
Zona horaria: America/Lima

## Objetivo

Aplicar los 28 contratos de accesibilidad definidos en la Etapa 2 contra los ocho repositorios EVA mediante evidencia de solo lectura, sin corregir archivos, asignar severidades ni iniciar la priorización.

## Método y límites

La ejecución `37798165287` clonó temporalmente los ocho repositorios públicos con permisos de lectura, ejecutó el scanner de línea base y publicó la evidencia como artefacto `11559462417`.

El análisis estático distingue entre:

- evidencia estructural automatizable que puede cerrarse de forma conservadora;
- candidatos que requieren validación de contexto, semántica o comportamiento;
- contratos que necesitan interacción, árbol de accesibilidad, medición visual o revisión humana controlada.

No se declara conformidad WCAG global a partir de esta etapa.

## Universo observado

La Etapa 1 conservaba una referencia de 65 HTML. La lectura actual encontró 66 HTML. La diferencia de +1 se conserva como variación del universo y **no se interpreta como fallo de accesibilidad ni se elimina para forzar el conteo histórico**.

## Resultado de los 28 contratos

- `CUMPLE`: 2
- `INCUMPLIMIENTO_CONFIRMADO`: 0
- `REQUIERE_VERIFICACION_CONTROLADA`: 26

Los dos resultados `CUMPLE` corresponden exclusivamente al componente estructural automatizable:

- `A11Y-CON-001`: 0 de 139 imágenes observadas carecen de atributo `alt`.
- `A11Y-CON-003`: 0 botones o enlaces observados carecen de nombre accesible estático según el scanner.

Estos resultados no sustituyen la revisión semántica de la calidad del texto alternativo ni de la adecuación del nombre al propósito del control.

## Candidatos específicos

### A11Y-CON-005 — formularios

Después de reconocer también etiquetas implícitas (`<label>...<input>...</label>`), quedó **1 candidato** para verificación controlada:

- `materiales-educativos-accesibles/pictogramas/pictogramas.html`

No se declara incumplimiento hasta comprobar el nombre accesible efectivo y cualquier etiquetado dinámico.

### A11Y-CON-009 y A11Y-CON-010 — idioma y título

La lectura estática detectó tres archivos sin `lang` y sin título no vacío:

- `crebeucayali.github.io/google09722cd21d5d281a.html`
- `accesos-complementarios/google09722cd21d5d281a.html`
- `banco-digital-accesible/docs/referencias/logo-ruta-base.html`

Por su naturaleza aparente de verificación/referencia auxiliar, se mantienen como `REQUIERE_VERIFICACION_CONTROLADA`; primero debe confirmarse si pertenecen al universo funcional accesible antes de convertirlos en hallazgo.

## Otros contratos

Los 23 contratos restantes requieren interacción, árbol de accesibilidad, medición visual o juicio semántico. Permanecen en `REQUIERE_VERIFICACION_CONTROLADA` sin inferir cumplimiento ni fallo desde HTML estático.

## Guardrails verificados

- 0 modificaciones en los ocho repositorios EVA.
- 0 modificaciones en Supabase.
- 0 correcciones aplicadas.
- 0 severidades asignadas.
- 0 priorización realizada.
- Etapa 4 no iniciada.

## Paso siguiente

La Etapa 4 podrá clasificar y organizar **solo la evidencia obtenida**, sin convertir automáticamente los 26 contratos pendientes en fallos. Las verificaciones interactivas/controladas corresponden a la etapa prevista para pruebas controladas.
