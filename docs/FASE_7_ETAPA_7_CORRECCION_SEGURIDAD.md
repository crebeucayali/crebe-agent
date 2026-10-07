# Fase 7 — Etapa 7: Corrección controlada de seguridad

Estado: `ETAPA_7_EN_CURSO_CON_BLOQUEOS_CONTROLADOS`.

## Modelo de autenticación
- `master`: autenticado + AAL2/MFA obligatorio para operaciones sensibles y gestión de usuarios.
- `editor`: autenticado; AAL1 o AAL2, limitado a módulos asignados. No se impone MFA obligatorio en esta etapa.
- `consulta`: autenticado; AAL1 o AAL2, limitado a módulos asignados.

## 1. Default privileges + Data API — ALTO
El owner `postgres` quedó endurecido y verificado. Los defaults propiedad de `supabase_admin` siguen pendientes porque la sesión disponible no puede modificarlos.

## 2. `galeria_item_imagenes` — MEDIO
Corregido y verificado: `anon` conserva solo `SELECT`; `authenticated` conserva `SELECT`, `INSERT`, `UPDATE` y `DELETE`; RLS permanece intacto.

## 3. Leaked Password Protection — MEDIO
El subpunto fue intentado y verificado contra las capacidades y el plan actuales. La organización Supabase `crebe ucayali` está en `free / tier_free`.

La documentación oficial de Supabase establece que **Leaked Password Protection está disponible únicamente en el plan Pro o superior**. Por tanto, este control no puede habilitarse en el estado actual del proyecto, aunque se utilice Dashboard o Management API.

Estado formal: `BLOQUEADO_POR_PLAN`.

No se modificó MFA, AAL, RLS ni permisos de editores como consecuencia de este bloqueo.

## Estado de cierre
La Etapa 7 no se marca completada porque siguen dos dependencias reales:
1. restringir los defaults del owner `supabase_admin` con una identidad autorizada;
2. disponer de un plan Supabase Pro o superior para poder habilitar Leaked Password Protection.

La Etapa 8 permanece sin iniciar.
