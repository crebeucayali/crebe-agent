# Fase 8 — Etapa 5: Pruebas controladas de accesibilidad

Estado final: `ETAPA_5_COMPLETADA_PRUEBAS_CONTROLADAS_ACCESIBILIDAD`.

## Objetivo

Ejecutar verificaciones controladas sobre los 26 contratos pendientes de la Etapa 4, respetando el orden P0 → P1 → P2 y sin aplicar correcciones.

## Alcance y guardrails

- Solo lectura sobre los ocho repositorios EVA publicados.
- Sin cambios en Supabase.
- Sin autenticación administrativa.
- Sin envío de formularios ni acciones de escritura.
- Sin correcciones de HTML, CSS o JavaScript.
- Sin asignación de severidad en esta etapa.
- Etapa 6 no iniciada.

## Método

Las pruebas se ejecutaron mediante Chromium temporal con Playwright y `axe-core`. La inyección de `axe-core` requiere `bypassCSP` únicamente dentro del contexto de navegador de auditoría; este mecanismo **no modifica la Content Security Policy publicada de EVA**.

Se observaron 66 HTML. Tres corresponden a archivos auxiliares ya identificados en la Etapa 3 y permanecen en la evidencia, pero no se agregan como incumplimientos funcionales de EVA. El universo funcional probado quedó en 63 páginas, todas completadas y sin páginas no cargadas.

## Resultado de contratos pendientes

De los 26 contratos sometidos a verificación:

- 22 permanecen en `REQUIERE_DIAGNOSTICO_O_REVISION_MANUAL`;
- 1 queda en `INCUMPLIMIENTO_CONFIRMADO_AUTOMATIZADO`;
- 1 presenta `EVIDENCIA_FAVORABLE_CONTROLADA`;
- 1 queda en `REQUIERE_DIAGNOSTICO`;
- 1 resulta `NO_APLICA_EN_UNIVERSO_OBSERVADO`.

### A11Y-CON-013 — Navegación por teclado

En las 63 páginas funcionales hubo elementos enfocables y el primer `Tab` alcanzó un elemento enfocable en las 63. No se observaron páginas en las que esa comprobación inicial fallara.

Estado: `EVIDENCIA_FAVORABLE_CONTROLADA`.

Este resultado no certifica por sí mismo el recorrido completo, el orden de foco, ausencia de trampas o la visibilidad del foco; esos aspectos continúan sujetos a revisión donde corresponda.

### A11Y-CON-023 — Contraste

`axe-core` reportó 77 nodos asociados a `color-contrast` en páginas funcionales EVA.

Estado: `INCUMPLIMIENTO_CONFIRMADO_AUTOMATIZADO`.

El contrato pasa a Etapa 6 para identificar los selectores, combinaciones de color, componentes repetidos y alcance real antes de proponer cualquier cambio. En Etapa 5 no se asigna severidad ni se corrige.

### A11Y-CON-025 — Reflujo/móvil

A 320 px se detectó desbordamiento horizontal en cuatro páginas:

1. `accesos-complementarios/paginas/contacto.html`
2. `accesos-complementarios/recursos/contacto.html`
3. `banco-digital-accesible/braille/teoria.html`
4. `materiales-educativos-accesibles/generador/generador.html`

Estado: `REQUIERE_DIAGNOSTICO`.

La Etapa 6 deberá determinar causa, alcance y relación con pendientes históricos antes de considerar correcciones.

### A11Y-CON-027 — Multimedia

No se observaron elementos `video` o `audio` en las 63 páginas funcionales completamente probadas.

Estado: `NO_APLICA_EN_UNIVERSO_OBSERVADO`.

Este estado debe reabrirse si EVA incorpora multimedia en el futuro.

## Evidencia reproducible

- Workflow: `Accesibilidad EVA - Fase 8 Etapa 5`
- Run final: `37803532344`
- Artefacto: `11561852492`

## Criterio de cierre

La etapa queda cerrada porque:

1. se respetó el orden P0 → P1 → P2;
2. las 63 páginas funcionales fueron completamente probadas;
3. los tres HTML auxiliares fueron separados correctamente del agregado de fallos EVA;
4. los resultados se conservaron como evidencia reproducible;
5. no se modificó EVA ni Supabase;
6. no se aplicaron correcciones ni severidades;
7. la Etapa 6 permanece sin iniciar.
