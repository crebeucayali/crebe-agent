# Fase 8 — Etapa 8: Verificación y monitoreo de accesibilidad

Estado: `MONITOREO_ACCESIBILIDAD_ACTIVO`.

## Objetivo

Cerrar la secuencia de trabajo de la Fase 8 con una verificación independiente posterior a las correcciones de la Etapa 7 y dejar activo un monitoreo recurrente de regresiones automatizadas de accesibilidad.

## Verificación independiente inicial

La ejecución `38283434340` del workflow `Accesibilidad EVA - Fase 8 Etapa 8` finalizó correctamente y generó el artefacto `11761884219`.

Resultado observado:

- 63 páginas funcionales verificadas;
- 0 fallos de carga;
- 0 nodos con regresión de contraste;
- 4 objetivos de reflujo a 320 px verificados;
- 0 objetivos con overflow horizontal.

La verificación se ejecutó en modo de solo lectura. No modificó repositorios EVA ni Supabase.

## Monitoreo recurrente

Queda activo `.github/workflows/accessibility-monitor.yml`, con ejecución manual, en pull requests que afecten al propio monitor o al estado de la Fase 8 y con programación diaria a las `11:45 UTC` (`06:45` en America/Lima).

El monitor:

- carga las páginas funcionales públicas de los ocho repositorios EVA;
- detecta regresiones automatizadas de contraste mediante `axe-core`;
- comprueba los cuatro objetivos de reflujo diagnosticados y corregidos en las Etapas 6 y 7;
- genera evidencia en `reports/accessibility-monitor/resultado.json`;
- falla de forma visible si aparecen páginas no cargadas, nodos de contraste, objetivos de reflujo no observados o overflow horizontal.

Sus permisos se mantienen en `contents: read` y no contiene pasos de escritura sobre EVA o Supabase.

## Alcance y límite de la evidencia

La activación del monitoreo no equivale a una certificación WCAG integral. Permanecen 22 contratos en revisión manual sin fallo confirmado procedentes de las etapas anteriores. El monitor automatizado no los convierte en fallos ni los declara conformes.

Por tanto, el estado `MONITOREO_ACCESIBILIDAD_ACTIVO` significa que las regresiones automatizables incluidas en el alcance actual quedan vigiladas de manera recurrente y que las nueve causas corregidas en la Etapa 7 no presentan residuos en la verificación independiente inicial.

## Estado final de la Fase 8

Las Etapas 1 a 7 permanecen cerradas con su evidencia histórica. La Etapa 8 queda activa como capa permanente de verificación y monitoreo.

No se autorizan correcciones automáticas. Si el monitor detecta una regresión, corresponde registrar y diagnosticar el hallazgo antes de cualquier modificación.
