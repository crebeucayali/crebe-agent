# Fase 5, Etapa 6: corrección controlada

## Objetivo

Aplicar únicamente correcciones cuya causa raíz y solución estén suficientemente determinadas en la Etapa 5, manteniendo una intervención mínima y trazable.

## Regla operativa

`un problema -> una intervención -> una revisión de diff -> un merge -> verificación posterior en Etapa 7`

La Etapa 6 no declara una corrección como verificada en producción. Tras el merge, el estado correcto es `CORREGIDO_PENDIENTE_VERIFICACION`.

## Corrección 1 — Contacto institucional

Hallazgo: `F5E4-A1AE3BB801`.

Causa: `REFERENCIA_OBSOLETA_RUTA_CONTACTO`.

Repositorio intervenido: `crebeucayali/noti-inclusivos`.

PR: `#3`.

Merge commit: `b859109e1af623960628b9f1f6ef4a3a4a5d103c`.

Cambio aplicado: se sustituyeron exclusivamente las referencias a:

`https://crebeucayali.github.io/accesos-complementarios/institucional/contacto.html`

por:

`https://crebeucayali.github.io/accesos-complementarios/paginas/contacto.html`

El diff del PR comprende 8 archivos, 16 adiciones y 16 eliminaciones; las diferencias corresponden únicamente a las 16 referencias de Contacto diagnosticadas.

Estado al cierre de Etapa 6: `CORREGIDO_PENDIENTE_VERIFICACION`.

## Corrección 2 — Archivo de publicaciones

Hallazgo: `F5E4-E9B33D5047`.

Causa: `REFERENCIA_OBSOLETA_INDICE_PUBLICACIONES`.

Repositorio intervenido: `crebeucayali/noti-inclusivos`.

PR: `#4`.

Merge commit: `6672b18d459cd73f3761982f68b6dbd90c28ec84`.

Corrección aplicada: se creó `blog/index.html` como ruta de compatibilidad. La ruta histórica `/noti-inclusivos/blog/` redirige a `/noti-inclusivos/articulos/` y conserva un enlace visible de respaldo.

Se eligió la redirección de compatibilidad porque resuelve el 404 y, al mismo tiempo, evita romper marcadores o enlaces externos que todavía utilicen la ruta histórica.

Estado al cierre de Etapa 6: `CORREGIDO_PENDIENTE_VERIFICACION`.

## Hallazgo no intervenido — Juegos Interactivos Accesibles

Hallazgo: `F5E4-EAE63AF520`.

Causa: `RUTA_HUERFANA_MODULO_NO_PUBLICADO`.

No existe un destino publicado verificable y la Etapa 5 determinó que se requiere una decisión funcional: restituir/publicar JIA o retirar/reemplazar sus referencias.

No se modifica ninguno de los cuatro repositorios donde actualmente aparecen esas referencias.

Estado: `BLOQUEADO_POR_DECISION_FUNCIONAL`.

## Límites

- No se modificó Supabase.
- No se modificaron autenticación, MFA, permisos, panel administrativo ni datos.
- No se intervino JIA sin una decisión funcional.
- La Etapa 6 no realiza la verificación de GitHub Pages posterior al despliegue.
- La Etapa 7 permanece sin iniciar.
