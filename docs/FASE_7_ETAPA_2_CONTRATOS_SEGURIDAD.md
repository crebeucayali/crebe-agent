# Fase 7 · Etapa 2 — Contratos de seguridad y mínimo privilegio

## Objetivo

Convertir el inventario de seguridad de la Etapa 1 en reglas objetivas y verificables antes de ejecutar la auditoría de seguridad.

Esta etapa **no corrige permisos**, **no modifica RLS**, **no cambia GRANT**, **no altera Auth** y **no escribe en Supabase**.

## Modelo de roles

- `anon`: visitante público no autenticado.
- `authenticated`: sesión Supabase válida sin asumir privilegio administrativo.
- `publicador`: usuario autorizado con módulos asignados, sin privilegios master.
- `master`: administrador autorizado; AAL2 obligatorio para operaciones sensibles.
- `service_role`: credencial exclusivamente server-side.

## Principios

1. RLS y GRANT se evalúan como capas distintas.
2. `authenticated` no equivale a autorizado.
3. Una clave `sb_publishable_` puede estar en frontend; `service_role`, `sb_secret_`, contraseñas y secretos equivalentes no.
4. `SECURITY DEFINER` solo se admite cuando está justificado, fuera de `public`, sin EXECUTE para `PUBLIC` y con validación interna.
5. La Data API solo debe exponer objetos necesarios y con mínimo privilegio.
6. El bucket `eva-publico` puede ser público para lectura; sus escrituras administrativas deben permanecer protegidas.
7. No se crea una policy solo para silenciar un advisor si el modelo seguro requiere acceso indirecto.
8. Ninguna corrección se autoriza antes de la auditoría, priorización, prueba y diagnóstico.

## Cobertura

Se definieron **26 contratos** sobre las seis superficies inventariadas en la Etapa 1 y controles transversales de secretos, RLS, métricas y administración.

### SEC-SURFACE-001 — `galeria_item_imagenes`

Se separa el privilegio de tabla del acceso efectivo por RLS. La auditoría deberá determinar si los GRANT amplios son innecesarios y si existe capacidad efectiva no deseada; no se asumirá vulnerabilidad solo por observar el GRANT.

### SEC-SURFACE-002 — Default privileges / Data API

Los objetos nuevos de `public` no deben depender de privilegios históricos amplios. Antes del **30 de octubre de 2026**, la auditoría deberá producir una decisión explícita sobre exposición, GRANT mínimo y RLS.

### SEC-SURFACE-003 — Funciones privilegiadas

Toda función `SECURITY DEFINER` debe permanecer fuera de `public`, sin EXECUTE por `PUBLIC`, y limitar su ejecución a los roles que realmente la necesitan. Las funciones administrativas ejecutables por `authenticated` deben validar autorización real internamente.

### SEC-SURFACE-004 — `admin_guard`

RLS habilitado sin policies no se clasifica automáticamente como defecto: puede ser un diseño deliberado para impedir acceso directo y permitir únicamente funciones controladas. La Etapa 3 deberá verificarlo.

### SEC-SURFACE-005 — Auth

La protección contra contraseñas filtradas se auditará como control de endurecimiento independiente. Master debe conservar AAL2 para operaciones sensibles; un publicador no puede escalar privilegios solo por estar autenticado.

### SEC-SURFACE-006 — Storage

`eva-publico` puede mantener lectura pública de activos. INSERT/UPDATE/DELETE deben quedar sujetos a autorización administrativa, MFA y carpetas funcionales permitidas.

## Estados para la Etapa 3

Cada contrato podrá resultar en:

- `CUMPLE`
- `INCUMPLIMIENTO_CONFIRMADO`
- `REQUIERE_PRUEBA_CONTROLADA`
- `REQUIERE_REVISION_MANUAL`
- `NO_APLICA`

La Etapa 2 no asigna severidad y no genera todavía una cola de correcciones.

## Cierre

Estado: `ETAPA_2_COMPLETADA_CONTRATOS_SEGURIDAD`.

Supabase modificado: **no**.
Repositorios EVA modificados: **no**.
Etapa 3 iniciada: **no**.
