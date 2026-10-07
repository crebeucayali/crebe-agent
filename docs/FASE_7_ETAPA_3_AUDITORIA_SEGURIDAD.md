# Fase 7 — Etapa 3: Auditoría de seguridad de solo lectura

## Estado

`ETAPA_3_COMPLETADA_LINEA_BASE_SEGURIDAD`

## Objetivo

Comparar los 26 contratos de seguridad y mínimo privilegio definidos en la Etapa 2 contra el estado real de Supabase y los ocho repositorios EVA, sin modificar configuración, datos, RLS, GRANT, Storage, Auth ni código EVA.

## Resultado global

- Contratos auditados: 26.
- `CUMPLE`: 16.
- `INCUMPLIMIENTO_CONFIRMADO`: 5.
- `REQUIERE_PRUEBA_CONTROLADA`: 5.
- `REQUIERE_REVISION_MANUAL`: 0.
- `NO_APLICA`: 0.

## Incumplimientos confirmados

1. `SEC-CON-001`: `public.galeria_item_imagenes` conserva privilegios de tabla para `anon` y `authenticated` más amplios de lo necesario. RLS limita el acceso efectivo, pero no elimina el incumplimiento de mínimo privilegio en la capa GRANT.
2. `SEC-CON-003`: los default privileges de nuevas tablas en `public` siguen concediendo privilegios amplios a `anon` y `authenticated`.
3. `SEC-CON-004`: los default privileges de funciones nuevas en `public` siguen concediendo `EXECUTE` por defecto a `anon` y `authenticated`.
4. `SEC-CON-011`: Supabase Security Advisor informa que la protección contra contraseñas filtradas está deshabilitada.
5. `SEC-CON-026`: aunque la decisión sobre Data API ya está documentada, el estado actual todavía depende de default ACL amplios y debe resolverse antes del 30 de octubre de 2026.

Ninguno de estos hallazgos se corrige en esta etapa. La severidad se asignará en Etapa 4.

## Elementos que requieren prueba controlada

- `SEC-CON-007`: autorización efectiva de funciones `SECURITY DEFINER` con sesiones/roles reales.
- `SEC-CON-012`: rechazo master AAL1 y aceptación AAL2 en operaciones sensibles.
- `SEC-CON-013`: aislamiento por módulos para publicador y ausencia de escalación.
- `SEC-CON-015`: bloqueo efectivo de DML anónimo sobre `storage.objects` pese a grants de infraestructura.
- `SEC-CON-023`: gestión de usuarios/invitaciones reservada a master AAL2 y protección frente a escalación.

Estas pruebas corresponden a la Etapa 5, después de la priorización de la Etapa 4.

## Controles confirmados

- 19 funciones `SECURITY DEFINER` en `private`; 0 en `public`.
- 0 funciones `private SECURITY DEFINER` ejecutables por `PUBLIC`.
- `contador_visitas_eva_publico` es la única función privilegiada deliberadamente ejecutable por `anon` dentro del conjunto privado auditado.
- `calendario_publico` conserva `security_invoker=true`.
- Las 10 tablas funcionales `public` auditadas tienen RLS habilitado.
- `admin_guard` mantiene RLS sin policies, pero `anon` no tiene USAGE al schema ni acceso directo a sus tablas; no se crearán policies solo para silenciar el advisor.
- `eva-publico` conserva lectura pública; sus policies administrativas de escritura exigen sesión autenticada, MFA y carpetas admitidas.
- No se encontraron literales `sb_secret_` en los ocho repositorios EVA.
- `SUPABASE_SERVICE_ROLE_KEY` se obtiene desde entorno server-side en la Edge Function de invitaciones; el valor no está escrito en el repositorio.
- Las RPC administrativas inspeccionadas conservan validación mediante `auth.uid()`, rol, módulo y/o AAL2 según la operación.

## Security Advisor

El advisor reportó:

- 1 `WARN`: protección contra contraseñas filtradas deshabilitada.
- 2 `INFO`: RLS habilitado sin policies en `admin_guard.admin_correos_autorizados` y `admin_guard.admin_usuarios_autorizados`.

Los dos `INFO` no se consideran incumplimientos por sí mismos, porque corresponden al modelo deliberado de acceso indirecto y bloqueado al cliente.

## Guardrails

- Auditoría exclusivamente de lectura.
- Sin `INSERT`, `UPDATE`, `DELETE`, DDL ni cambios de Auth.
- Sin modificación de RLS/GRANT.
- Sin cambios en Storage.
- Sin modificación de los ocho repositorios EVA.
- Ninguna corrección automática.
- Etapa 4 no se considera iniciada hasta cerrar formalmente esta etapa.
