# Fase 5, Etapa 5: diagnóstico técnico de hallazgos funcionales

## Objetivo

Determinar la causa técnica de los tres hallazgos priorizados en la Etapa 4, identificar los archivos afectados y establecer el destino o la decisión funcional necesaria antes de cualquier corrección.

## Fuente

La Etapa 5 consume el artefacto validado de la Etapa 4. No vuelve a recorrer de forma masiva los ocho repositorios EVA. La evidencia diagnóstica se verificó mediante búsquedas dirigidas de código y estructura de repositorios.

## Diagnósticos

### F5E4-A1AE3BB801 — Contacto institucional 404

Causa: `REFERENCIA_OBSOLETA_RUTA_CONTACTO`.

Las páginas de `noti-inclusivos` conservan la ruta antigua `/accesos-complementarios/institucional/contacto.html`. El recurso vigente existe en `/accesos-complementarios/paginas/contacto.html` y el mapa web de Accesos Complementarios utiliza esa ubicación.

Destino técnico identificado:

`https://crebeucayali.github.io/accesos-complementarios/paginas/contacto.html`

Estado: `DIAGNOSTICADO_LISTO_PARA_CORRECCION`.

### F5E4-EAE63AF520 — Juegos Interactivos Accesibles 404

Causa: `RUTA_HUERFANA_MODULO_NO_PUBLICADO`.

La ruta `/juegos-interactivos-accesibles/` continúa enlazada desde varias superficies, pero actualmente no existe un repositorio publicado con ese nombre dentro de los repositorios de `crebeucayali`. La documentación histórica aún menciona JIA como componente, por lo que existe una desalineación entre la arquitectura histórica y el conjunto publicado actual.

No se asigna un destino sustituto sin evidencia. La corrección deberá decidir entre restituir/publicar JIA o retirar/reemplazar sus referencias por un módulo vigente.

Estado: `DIAGNOSTICADO_REQUIERE_DECISION_FUNCIONAL`.

### F5E4-E9B33D5047 — Archivo de publicaciones de Noti Inclusivos 404

Causa: `REFERENCIA_OBSOLETA_INDICE_PUBLICACIONES`.

`accesos-complementarios/mapa-web.html` enlaza a `/noti-inclusivos/blog/`, pero Noti Inclusivos no posee una carpeta `blog`. El índice vigente de artículos publicados existe en `/noti-inclusivos/articulos/`.

Destino técnico identificado:

`https://crebeucayali.github.io/noti-inclusivos/articulos/`

Estado: `DIAGNOSTICADO_LISTO_PARA_CORRECCION`.

## Límites

Esta etapa no modifica los ocho repositorios EVA, no cambia enlaces, no crea redirecciones y no elimina referencias. El diagnóstico de JIA no inventa un destino sustituto.

## Criterio de cierre

La Etapa 5 puede cerrarse cuando los tres hallazgos tengan causa raíz identificada, evidencia suficiente, archivos afectados trazables, acción técnica definida y, cuando no exista un reemplazo verificable, una decisión funcional explícitamente pendiente. La Etapa 6 debe permanecer sin iniciar.
