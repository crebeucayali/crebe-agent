# Fase 8 — Etapa 4: Clasificación y priorización de accesibilidad

Estado: `ETAPA_4_COMPLETADA_PRIORIZACION_ACCESIBILIDAD`

## Objetivo

Clasificar y ordenar los 26 contratos que en la Etapa 3 quedaron como `REQUIERE_VERIFICACION_CONTROLADA`, sin convertir candidatos en fallos, sin aplicar correcciones y sin modificar EVA.

## Fuente

La única base de esta etapa es `reports/fase-8-etapa-3-linea-base-accesibilidad.json`.

La línea base cerró con:

- 28 contratos totales;
- 2 `CUMPLE` en comprobaciones estructurales automatizables;
- 0 `INCUMPLIMIENTO_CONFIRMADO`;
- 26 `REQUIERE_VERIFICACION_CONTROLADA`.

## Regla de priorización

La prioridad definida aquí corresponde al **orden de verificación de Etapa 5**. No equivale a una severidad de defecto, porque aún no existen fallos confirmados sobre estos 26 contratos.

### P0 — Operabilidad

11 contratos: `A11Y-CON-005`, `006`, `013`, `014`, `015`, `016`, `017`, `018`, `025`, `026`, `028`.

Se verifican primero porque pueden afectar formularios, errores, teclado, foco, diálogos, contenido dinámico, zoom/reflujo, controles móviles y componentes administrativos.

### P1 — Estructura y percepción

13 contratos: `A11Y-CON-002`, `004`, `007`, `008`, `009`, `010`, `011`, `012`, `019`, `020`, `021`, `023`, `024`.

Incluyen equivalencia semántica, nombre/rol/estado, encabezados, relaciones, idioma, títulos, landmarks, ARIA, tablas, contraste y uso del color.

### P2 — Contexto acotado

2 contratos: `A11Y-CON-022` y `A11Y-CON-027`.

Su prueba depende de confirmar presencia y uso real de tablas no tabulares o contenido multimedia.

## Candidatos específicos conservados

- `A11Y-CON-005`: un único candidato en `materiales-educativos-accesibles/pictogramas/pictogramas.html`; no se declara fallo hasta comprobar su nombre accesible efectivo.
- `A11Y-CON-009` y `A11Y-CON-010`: tres HTML candidatos que parecen archivos auxiliares de verificación o referencia; primero debe confirmarse que pertenecen al universo funcional.
- Universo HTML: referencia histórica 65, observación actual 66; la diferencia se conserva como objeto de verificación y no se fuerza ni se corrige.

## Guardrails

Durante esta etapa:

- no se modificó ninguno de los ocho repositorios EVA;
- no se modificó Supabase;
- no se aplicaron correcciones;
- no se asignó severidad a fallos no confirmados;
- no se inició Etapa 5;
- no se declaró conformidad WCAG.

## Siguiente etapa

La Etapa 5 ejecutará pruebas controladas siguiendo el orden P0 → P1 → P2. Solo la evidencia de esas pruebas podrá confirmar o descartar incumplimientos que después pasen a diagnóstico.
