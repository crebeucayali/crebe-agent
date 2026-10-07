# Fase 7 — Etapa 7: Corrección controlada de seguridad

Estado: `ETAPA_7_EN_CURSO_CON_BLOQUEOS_CONTROLADOS`.

La etapa se inició sobre los tres hallazgos diagnosticados en la Etapa 6. Se aplicaron únicamente cambios mínimos y verificables, sin relajar RLS, sin revocaciones masivas de objetos existentes y sin modificar los ocho repositorios EVA.

## 1. Default privileges + Data API — ALTO

### Aplicado
- Owner `postgres`: se retiraron de `anon` y `authenticated` los default privileges futuros sobre tablas, secuencias y funciones en `public`.
- Se retiró además `EXECUTE` futuro vía `PUBLIC` para funciones creadas por `postgres`.
- La prueba inicial detectó correctamente que `PUBLIC` seguía otorgando `EXECUTE`; esa prueba falló y revirtió completamente.
- Tras ajustar el default global de funciones, una nueva tabla y una nueva función de prueba confirmaron que `anon` y `authenticated` ya no heredan acceso. Los objetos de prueba se eliminaron en la misma migración.

### Bloqueo pendiente
Los default privileges de objetos cuyo owner es `supabase_admin` siguen otorgando permisos amplios. La sesión disponible opera como `postgres`, no es miembro de `supabase_admin` y PostgreSQL rechazó el cambio con `permission denied to change default privileges`.

No se intentó escalar privilegios ni cambiar ownership.

## 2. `galeria_item_imagenes` — MEDIO

Corregido y verificado:
- `anon`: solo `SELECT`.
- `authenticated`: `SELECT`, `INSERT`, `UPDATE`, `DELETE`.
- retirados de ambos roles: privilegios no necesarios como `TRUNCATE`, `REFERENCES` y `TRIGGER`.
- las cinco policies RLS se conservaron intactas.

Esto mantiene la lectura pública y el flujo administrativo existente sin ampliar permisos.

## 3. Leaked Password Protection — MEDIO

El Security Advisor continúa reportando `auth_leaked_password_protection` como `WARN`.

La capacidad Supabase disponible en esta ejecución permite migraciones SQL, consultas y lectura del Security Advisor, pero no expone escritura de la configuración de Auth/Management API. Por tanto, habilitar esta opción no puede ejecutarse de forma segura desde este conector y queda documentado como bloqueo de capacidad de plataforma, no como corrección omitida silenciosamente.

Referencia oficial: https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection

## Estado de cierre

La Etapa 7 no se marca completada porque quedan dos dependencias reales:
1. restringir los defaults del owner `supabase_admin` mediante una identidad autorizada;
2. habilitar Leaked Password Protection mediante Dashboard o Management API autorizada.

La Etapa 8 permanece sin iniciar.
