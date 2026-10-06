# Fase 7 — Seguridad, permisos y exposición de datos

## Objetivo

Auditar y reducir riesgos de exposición, privilegios excesivos y configuraciones inseguras en EVA y Supabase, preservando el funcionamiento validado en las Fases 5 y 6.

## Alcance

- 8 repositorios EVA.
- Proyecto Supabase `dteimbhwtzghhsijeeld`.
- RLS y políticas.
- GRANT y principio de mínimo privilegio.
- Data API y objetos expuestos.
- Storage y políticas de acceso.
- Funciones/RPC, en especial `SECURITY DEFINER`.
- Autenticación administrativa, sesión y AAL2/MFA.
- Rutas administrativas y superficies públicas.
- Búsqueda de secretos o credenciales privadas expuestas.
- Dependencias y servicios externos relevantes.

## Dependencia heredada

`SEC-DEPENDENCY-001`: revisar permisos potencialmente más amplios de lo necesario en `galeria_item_imagenes`.

## Reglas obligatorias

1. Las Etapas 1–4 son de solo lectura.
2. Una clave publicable de Supabase no se clasifica como secreto por sí sola.
3. Service-role, secretos privados, tokens administrativos o credenciales equivalentes sí son críticos y nunca deben copiarse en claro a reportes, logs o chat.
4. La evidencia sensible se registra enmascarada o mediante huella/fingerprint.
5. No se desactiva ni relaja RLS para resolver fallos funcionales.
6. Ningún `GRANT` se amplía sin necesidad funcional demostrada.
7. No se ejecuta corrección automática.
8. Toda corrección requiere: evidencia → clasificación → diagnóstico → intervención mínima → prueba de regresión.
9. Un mismo origen causal genera un solo hallazgo aunque afecte varias páginas u objetos.

## Etapas

### 1. Inventario de superficie de seguridad
Mapear repositorios, claves/configuración pública, tablas/vistas, RLS, políticas, grants, funciones, Storage, autenticación y rutas administrativas.

### 2. Contratos de seguridad y mínimo privilegio
Definir qué puede hacer `anon`, un usuario autenticado sin privilegios y un administrador autorizado; qué objetos deben ser públicos y cuáles deben quedar bloqueados.

### 3. Auditoría de solo lectura
Buscar secretos, políticas permisivas, RLS ausente, grants excesivos, funciones privilegiadas, Storage demasiado abierto, exposición Data API y debilidades de autenticación/configuración.

### 4. Clasificación y priorización
Estados: `CRITICO`, `ALTO`, `MEDIO`, `BAJO`. No se prioriza por cantidad de ocurrencias sino por impacto y explotabilidad.

### 5. Pruebas controladas de permisos
Validar acceso real como anónimo, autenticado no administrador y administrador autorizado. Las pruebas que escriban datos deberán ser reversibles, identificables y no publicadas.

### 6. Diagnóstico técnico
Determinar causa exacta, objeto afectado y cambio mínimo necesario.

### 7. Corrección controlada
Aplicar únicamente cambios diagnosticados: RLS/policies, REVOKE/GRANT, funciones, Storage, credenciales o configuración administrativa. Nunca mezclar correcciones independientes.

### 8. Verificación y monitoreo
Revalidar seguridad y funcionalidad. Activar controles recurrentes de solo lectura cuando sean seguros y no requieran secretos privilegiados.

## Condición temporal prioritaria

Antes del **30 de octubre de 2026** debe verificarse la exposición de objetos por Data API, los grants realmente necesarios y la interacción con RLS, sin ampliar permisos por conveniencia.

## Estado inicial

`FASE_7_PREPARADA`

La Etapa 1 permanece sin iniciar hasta cerrar y fusionar esta preparación.
