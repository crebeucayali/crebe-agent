# Fase 7 · Etapa 5 — Pruebas controladas de permisos

Estado: `ETAPA_5_COMPLETADA_PRUEBAS_PERMISOS`.

## Objetivo

Resolver mediante pruebas efectivas los cinco contratos que en la Etapa 3 quedaron como `REQUIERE_PRUEBA_CONTROLADA`, sin dejar cambios persistentes en producción.

## Método

Las pruebas se ejecutaron directamente contra Supabase usando sesiones/claims controlados y transacciones con `ROLLBACK` total. No se registraron correos, UUID, tokens ni secretos en la evidencia.

## Resultados

| Contrato | Resultado | Evidencia |
|---|---|---|
| `SEC-CON-007` | PASS | `authenticated` sin autorización administrativa fue rechazado por una RPC protegida. |
| `SEC-CON-012` | PASS | master con AAL1 fue rechazado; la misma sesión master con AAL2 fue aceptada. |
| `SEC-CON-013` | PASS | un editor limitado temporalmente a `noticias` pudo acceder a ese módulo, fue bloqueado en `galeria` y no obtuvo escritura master. |
| `SEC-CON-015` | PASS | `anon` no pudo insertar, actualizar ni eliminar objetos de `eva-publico`. |
| `SEC-CON-023` | PASS | un editor no pudo autorizar invitaciones ni gestionar usuarios. |

Resultado global: **5/5 contratos aprobados**.

## Guardrails

- Todos los cambios temporales se ejecutaron dentro de transacciones revertidas.
- No quedó ningún cambio de módulos de usuarios.
- No se creó ningún usuario real de prueba.
- No se dejó ningún objeto en Storage.
- No se modificaron RLS, policies, GRANT ni default privileges.
- No se modificó ninguno de los ocho repositorios EVA.

## Hallazgos que continúan abiertos

Las pruebas controladas no eliminan los tres hallazgos causales priorizados en la Etapa 4:

1. `F7S4-DEFAULT-PRIVILEGES-DATA-API` — ALTO.
2. `F7S4-GALERIA-GRANTS` — MEDIO.
3. `F7S4-AUTH-LEAKED-PASSWORD` — MEDIO.

Esos hallazgos pasan a diagnóstico técnico en la Etapa 6. Esta etapa no autoriza correcciones.
