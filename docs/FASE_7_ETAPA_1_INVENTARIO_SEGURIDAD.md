# Fase 7 — Etapa 1: Inventario de superficie de seguridad

## Objetivo

Levantar la superficie real de seguridad de EVA y Supabase antes de definir contratos, clasificar riesgos o autorizar correcciones.

## Método

La etapa se ejecutó en modo `READ_ONLY` mediante:

- catálogos PostgreSQL de Supabase;
- `pg_policies`, ACL/GRANT, funciones y schemas;
- Supabase Security Advisor;
- revisión del bucket `eva-publico`;
- búsqueda de código en los 8 repositorios EVA;
- revisión del changelog vigente de Supabase para Data API.

No se ejecutaron migraciones, cambios de RLS/GRANT, escrituras de datos ni modificaciones en los repositorios EVA.

## Inventario Supabase

Se catalogaron cuatro schemas relevantes: `public`, `private`, `admin_guard` y `storage`.

La fotografía estructural contiene 21 objetos relevantes: 11 en `public`, 2 en `admin_guard` y 8 en `storage`. Se registraron 36 políticas RLS sobre los objetos funcionales y Storage.

`public.calendario_publico` continúa con `security_invoker=true`.

El bucket `eva-publico` es público, mantiene límite de 5 MiB y admite WebP, JPEG y PNG. Las escrituras observadas sobre `storage.objects` se restringen mediante políticas para usuarios autenticados, MFA y carpetas funcionales.

### Funciones

No se observaron funciones `SECURITY DEFINER` en `public`.

En `private` se catalogaron 24 funciones, 19 de ellas `SECURITY DEFINER`. Ninguna de las funciones privadas inventariadas concede `EXECUTE` a `PUBLIC`. Algunas se exponen deliberadamente a `authenticated` para flujos administrativos y deberán evaluarse contra contratos de rol en las Etapas 2 y 3.

### Advisor

El Security Advisor informa:

- RLS habilitado sin policies en `admin_guard.admin_correos_autorizados`;
- RLS habilitado sin policies en `admin_guard.admin_usuarios_autorizados`;
- protección de contraseñas filtradas deshabilitada.

En esta etapa no se clasifican como vulnerabilidad confirmada. El inventario también constató que `anon` no tiene `USAGE` en `admin_guard` y que las tablas observadas allí mantienen grants de tabla para `service_role`, por lo que el contexto completo debe evaluarse antes de intervenir.

## Superficies que pasan a contratos/auditoría

1. `SEC-SURFACE-001`: `galeria_item_imagenes` mantiene grants de tabla amplios para `anon` y `authenticated`, aunque existen políticas RLS específicas. Hereda `SEC-DEPENDENCY-001`.
2. `SEC-SURFACE-002`: los default privileges históricos de `public` siguen otorgando privilegios amplios a nuevos objetos. Debe revisarse junto al cambio Data API previsto para el 30-10-2026.
3. `SEC-SURFACE-003`: funciones `SECURITY DEFINER` en `private` y roles autorizados para ejecutarlas.
4. `SEC-SURFACE-004`: tablas `admin_guard` con RLS sin policies y su modelo de aislamiento por schema/grants.
5. `SEC-SURFACE-005`: protección de contraseñas filtradas deshabilitada.
6. `SEC-SURFACE-006`: bucket público `eva-publico`, separación entre lectura pública y escrituras administrativas.

Estas entradas son superficies inventariadas, no severidades ni hallazgos priorizados.

## GitHub y secretos

La búsqueda en los repositorios EVA no encontró literales `sb_secret_`.

Las apariciones de `SUPABASE_SERVICE_ROLE_KEY` observadas corresponden a:

- lectura desde variable de entorno en la Edge Function server-side `admin-invitar-editor`;
- pruebas con valores sintéticos;
- documentación y SQL de permisos.

No se registró ningún valor secreto en este artefacto.

La clave `sb_publishable_...` aparece en frontend, lo cual es esperado para una clave publicable y no se clasifica por sí sola como exposición de secreto.

La autenticación administrativa observada usa Supabase Auth, autorización por rol/módulo y MFA; la documentación existente exige AAL2 para master y operaciones administrativas sensibles.

No se encontró referencia directa al proyecto Supabase en `DUA-3.0` mediante la búsqueda ejecutada; esto no implica ausencia de dependencias indirectas compartidas y se conservará como dato del inventario.

## Data API — condición temporal

Supabase anunció que el 30 de octubre de 2026 aplicará a proyectos existentes el cambio por el cual los nuevos objetos de `public` dejan de exponerse automáticamente a Data API si no tienen grants explícitos. Los objetos existentes conservan sus grants actuales. La Etapa 2 deberá definir qué grants son realmente necesarios por rol antes de cualquier revocación.

## Cierre

Estado: `ETAPA_1_COMPLETADA_INVENTARIO_SEGURIDAD`.

La siguiente etapa es `Contratos de seguridad y mínimo privilegio`. No se autoriza ninguna corrección a partir de este inventario por sí solo.
