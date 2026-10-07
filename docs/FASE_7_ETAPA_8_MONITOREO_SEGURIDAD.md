# Fase 7 — Etapa 8: Verificación y monitoreo de seguridad

Estado objetivo: `MONITOREO_SEGURIDAD_ACTIVO`.

## Verificación profunda de activación

Se confirmó en Supabase:

- todas las tablas funcionales de `public` conservan RLS habilitado;
- las tablas de `admin_guard` conservan RLS habilitado;
- `galeria_item_imagenes`: `anon` conserva solo `SELECT`;
- `galeria_item_imagenes`: `authenticated` conserva `SELECT`, `INSERT`, `UPDATE`, `DELETE`;
- los default ACL del owner `postgres` en `public` ya no incluyen `anon` ni `authenticated`; solo permanecen `postgres` y `service_role` según tipo de objeto;
- no existen objetos de `public` propiedad de `supabase_admin`.

Security Advisor mantiene únicamente:

1. dos hallazgos `INFO` de `admin_guard` con RLS y sin policies, esperados por el modelo de aislamiento mediante schema/grants y funciones controladas;
2. `Leaked Password Protection Disabled` como `WARN`, aceptado como `ACEPTADO_NO_APLICABLE_EN_PLAN_FREE` mientras la organización permanezca en Supabase Free.

## Monitoreo recurrente

GitHub Actions ejecuta `security_monitor.py` diariamente a las 06:15 de Lima (`15 11 * * *`) y también de forma manual o ante cambios relevantes mediante pull request.

El monitor recurrente no almacena credenciales de Supabase. Comprueba:

- que Etapa 7 siga formalmente completada;
- que Data API/default privileges y Galería sigan en `CORREGIDO_VERIFICADO`;
- que la excepción de Leaked Password Protection permanezca explícita y condicionada al plan Free;
- que master conserve AAL2/MFA obligatorio;
- que no se imponga MFA a editores sin decisión separada;
- que no aparezcan claves literales con prefijo `sb_secret_` en el repositorio.

Las verificaciones profundas de Advisor, catálogos, RLS, GRANT y ownership se ejecutan mediante conexión controlada cuando haya cambios de seguridad, migraciones relevantes, cambio de plan o una alerta recurrente.

## Criterio de alerta

La excepción de Leaked Password Protection no genera alerta mientras el plan sea Free. Debe reabrirse si se migra a Pro o superior.

Los dos `INFO` de `admin_guard` deben reabrirse si cambia el aislamiento del schema, sus grants o aparece acceso directo no previsto.

No se modificó RLS, MFA/AAL ni permisos de editores durante esta etapa.
