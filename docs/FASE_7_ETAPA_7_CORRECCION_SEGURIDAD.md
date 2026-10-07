# Fase 7 — Etapa 7: Corrección controlada de seguridad

Estado: `ETAPA_7_COMPLETADA_CORRECCION_SEGURIDAD`.

## Modelo de autenticación
- `master`: autenticado + AAL2/MFA obligatorio para operaciones sensibles y gestión de usuarios.
- `editor`: autenticado; AAL1 o AAL2, limitado a módulos asignados. No se impone MFA obligatorio en esta etapa.
- `consulta`: autenticado; AAL1 o AAL2, limitado a módulos asignados.

## 1. Default privileges + Data API — ALTO

Estado: `CORREGIDO_VERIFICADO`.

El owner funcional de los objetos EVA en `public` es `postgres`. Sobre ese role se aplicó y verificó el endurecimiento recomendado para proyectos existentes: se retiraron default privileges futuros innecesarios para `anon` y `authenticated`, se retiró `EXECUTE` futuro vía `PUBLIC` y una prueba temporal confirmó que nuevos objetos ya no heredan acceso no deseado.

`supabase_admin` queda clasificado como rol interno gestionado por Supabase. No existen objetos funcionales EVA de `public` propiedad de ese role, por lo que no existe corrección pendiente de EVA sobre sus ACL internas.

## 2. `galeria_item_imagenes` — MEDIO

Estado: `CORREGIDO_VERIFICADO`.

- `anon`: solo `SELECT`.
- `authenticated`: `SELECT`, `INSERT`, `UPDATE`, `DELETE`.
- retirados `TRUNCATE`, `REFERENCES` y `TRIGGER`.
- RLS permanece intacto.

## 3. Leaked Password Protection — MEDIO

Estado: `ACEPTADO_NO_APLICABLE_EN_PLAN_FREE`.

La organización Supabase permanece deliberadamente en `free / tier_free`. Leaked Password Protection requiere Pro o superior. El usuario decidió mantener el plan Free, por lo que este control no se considera una deuda accionable ni un bloqueo para el cierre de la etapa.

No se simula su activación y no se modifica MFA, AAL, RLS ni permisos de editores. La excepción queda documentada y solo deberá reabrirse si en el futuro la organización migra a Supabase Pro o superior.

## Cierre

Resultado final de los tres hallazgos:
- 2 `CORREGIDO_VERIFICADO`;
- 1 `ACEPTADO_NO_APLICABLE_EN_PLAN_FREE`;
- 0 parcialmente corregidos;
- 0 bloqueos técnicos accionables.

Los criterios de cierre de la Etapa 7 se consideran cumplidos. La Etapa 8 queda disponible para iniciar la verificación y monitoreo de seguridad.
