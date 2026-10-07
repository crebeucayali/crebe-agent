# Fase 7 — Etapa 6: Diagnóstico técnico de seguridad

Estado: `ETAPA_6_COMPLETADA_DIAGNOSTICO_SEGURIDAD`

## Alcance

Diagnosticar los tres hallazgos causales priorizados en la Etapa 4 usando la evidencia de la auditoría y de las pruebas controladas de la Etapa 5. Esta etapa no autoriza ni ejecuta correcciones.

## Resultado

### 1. F7S4-DEFAULT-PRIVILEGES-DATA-API — ALTO

La causa raíz son los default ACL del schema `public` para los owners `postgres` y `supabase_admin`. Actualmente las futuras tablas, funciones y secuencias pueden heredar privilegios amplios para `anon` y `authenticated`.

Corrección mínima propuesta para Etapa 7: cambiar exclusivamente los **default privileges futuros**, sin mezclar en el mismo paso revocaciones masivas de permisos sobre objetos existentes. Después se debe comprobar con un objeto temporal y reversible que la herencia ya no ocurra.

Fecha objetivo: antes del **2026-10-30**.

### 2. F7S4-GALERIA-GRANTS — MEDIO

`public.galeria_item_imagenes` tiene grants completos para `anon` y `authenticated`. RLS evita actualmente el abuso y las pruebas de Etapa 5 confirmaron que los controles efectivos funcionan.

El frontend público requiere `SELECT`. El panel administrativo usa acceso directo a la tabla, por lo que `authenticated` necesita conservar `SELECT/INSERT/UPDATE/DELETE` mientras esas operaciones sigan protegidas por RLS y AAL2.

Corrección mínima propuesta:

- `anon`: conservar únicamente `SELECT`; revocar `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `REFERENCES` y `TRIGGER`.
- `authenticated`: conservar `SELECT`, `INSERT`, `UPDATE`, `DELETE`; revocar `TRUNCATE`, `REFERENCES` y `TRIGGER`.
- no modificar RLS.

### 3. F7S4-AUTH-LEAKED-PASSWORD — MEDIO

Supabase Security Advisor continúa reportando `auth_leaked_password_protection` como `WARN`. La causa es una opción de Auth deshabilitada, no un fallo de RLS o del panel.

Corrección mínima propuesta: habilitar **Leaked Password Protection** sin tocar MFA/AAL2 ni permisos de base de datos. Después se debe verificar que el warning desaparezca y que el acceso administrativo siga operativo.

## Evidencia de Etapa 5

Los cinco contratos que requerían prueba controlada fueron aprobados: identidad no autorizada rechazada, master AAL1 rechazado y AAL2 aceptado, editor aislado por módulo, DML anónimo en Storage bloqueado y escalación administrativa bloqueada. No dejaron residuos.

## Orden para Etapa 7

1. Default privileges + Data API.
2. Grants de `galeria_item_imagenes`.
3. Leaked Password Protection.

Cada intervención deberá verificarse antes de continuar con la siguiente. No se autoriza una revocación masiva ni una relajación de RLS.
