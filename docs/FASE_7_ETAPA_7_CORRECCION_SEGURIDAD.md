# Fase 7 — Etapa 7: Corrección controlada de seguridad

Estado: `ETAPA_7_EN_CURSO_CON_BLOQUEOS_CONTROLADOS`.

## Modelo de autenticación
- `master`: autenticado + AAL2/MFA obligatorio para operaciones sensibles y gestión de usuarios.
- `editor`: autenticado; AAL1 o AAL2, limitado a módulos asignados. No se impone MFA obligatorio en esta etapa.
- `consulta`: autenticado; AAL1 o AAL2, limitado a módulos asignados.

## 1. Default privileges + Data API — ALTO

Estado: `CORREGIDO_VERIFICADO`.

El owner funcional de los objetos EVA en `public` es `postgres`. Sobre ese role ya se aplicó el endurecimiento recomendado para proyectos existentes:

- retirados los default privileges futuros innecesarios para `anon` y `authenticated` sobre tablas, secuencias y funciones;
- retirado `EXECUTE` futuro heredado mediante `PUBLIC` para funciones creadas por `postgres`;
- prueba temporal de tabla y función nuevas confirmó que ya no heredan acceso no deseado.

La documentación oficial de Supabase indica precisamente aplicar este cambio mediante `ALTER DEFAULT PRIVILEGES FOR ROLE postgres` en proyectos existentes.

Además se verificó el catálogo real de `public`: no existe ningún objeto funcional EVA propiedad de `supabase_admin`. Supabase documenta `supabase_admin` como un rol interno utilizado para tareas administrativas, upgrades y automatizaciones. Por tanto, sus ACL internas no se consideran una corrección pendiente de EVA y no se intenta escalar privilegios para modificarlas.

## 2. `galeria_item_imagenes` — MEDIO

Estado: `CORREGIDO_VERIFICADO`.

- `anon`: solo `SELECT`.
- `authenticated`: `SELECT`, `INSERT`, `UPDATE`, `DELETE`.
- retirados `TRUNCATE`, `REFERENCES` y `TRIGGER`.
- RLS permanece intacto.

## 3. Leaked Password Protection — MEDIO

Estado: `BLOQUEADO_POR_PLAN`.

La organización Supabase está en `free / tier_free`. La documentación oficial establece que Leaked Password Protection está disponible únicamente en Pro o superior.

No se modifica MFA, AAL, RLS ni permisos de editores como consecuencia de este bloqueo.

## Estado de cierre

La deuda técnica de Data API/default privileges queda cerrada. El único bloqueo restante de Etapa 7 es de plan:

1. `Leaked Password Protection` requiere Supabase Pro o superior.

La Etapa 8 permanece sin iniciar mientras se mantenga el criterio actual de no avanzar con bloqueos de seguridad pendientes.
