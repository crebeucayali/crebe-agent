# Fase 7 — Etapa 4: Clasificación y priorización de riesgos

Estado: `ETAPA_4_COMPLETADA_PRIORIZACION_SEGURIDAD`.

## Criterio

La Etapa 3 produjo 5 contratos con incumplimiento confirmado. La Etapa 4 no los cuenta mecánicamente como cinco fallos independientes: agrupa por causa técnica para evitar duplicidad.

## Resultado

Se obtienen 3 hallazgos causales:

1. `F7S4-DEFAULT-PRIVILEGES-DATA-API` — **ALTO**. Agrupa `SEC-CON-003`, `SEC-CON-004` y `SEC-CON-026`. La causa común son default privileges históricos amplios en `public` y la dependencia de exposición implícita de objetos nuevos. Debe resolverse antes del 2026-10-30.
2. `F7S4-GALERIA-GRANTS` — **MEDIO**. Corresponde a `SEC-CON-001`. RLS limita hoy el acceso efectivo, pero los GRANT de `galeria_item_imagenes` exceden el mínimo necesario.
3. `F7S4-AUTH-LEAKED-PASSWORD` — **MEDIO**. Corresponde a `SEC-CON-011`. Leaked Password Protection está deshabilitado.

No hay hallazgos `CRITICO` ni `BAJO` en esta línea base.

## Casos aún no clasificados definitivamente

Los contratos `SEC-CON-007`, `SEC-CON-012`, `SEC-CON-013`, `SEC-CON-015` y `SEC-CON-023` continúan como `REQUIERE_PRUEBA_CONTROLADA`. No se les asigna severidad definitiva y no entran a corrección antes de la Etapa 5.

## Guardrails

- No se cambia RLS, GRANT, Auth, Storage ni Data API en esta etapa.
- No se crea una policy solo para silenciar un advisor.
- No se debilita seguridad para conservar funcionalidad.
- La Etapa 4 prioriza; no diagnostica aún la forma exacta de corrección.
- Toda intervención futura requiere prueba/diagnóstico y verificación de regresión.

Supabase y los ocho repositorios EVA permanecen sin modificaciones.
