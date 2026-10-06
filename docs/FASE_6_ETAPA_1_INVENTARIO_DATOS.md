# Fase 6 · Etapa 1 — Inventario de datos y dependencias

## Estado

`ETAPA_1_COMPLETADA_INVENTARIO_DATOS`

## Objetivo

Construir una fotografía técnica y trazable, de solo lectura, de los objetos Supabase que sostienen los flujos dinámicos de EVA y de sus consumidores públicos/administrativos.

Esta etapa no determina todavía si los datos cumplen todos sus contratos funcionales. Los conteos observados son evidencia de inventario, no invariantes permanentes.

## Alcance y seguridad

- Proyecto: `dteimbhwtzghhsijeeld` (`crebe Project`).
- Estado observado: `ACTIVE_HEALTHY`.
- PostgreSQL: 17.
- No se ejecutaron `INSERT`, `UPDATE`, `DELETE`, DDL, cambios RLS, Storage writes ni cambios de Auth.
- No se modificó ninguno de los ocho repositorios EVA.
- No se almacenan claves Supabase ni credenciales en el repositorio del agente.

## Objetos inventariados

Se inventariaron 12 objetos funcionales principales:

1. `public.calendario_actividades`
2. `public.calendario_publico`
3. `public.capacitaciones_sesiones`
4. `public.noticias_destacadas`
5. `public.galeria_items`
6. `public.galeria_item_imagenes`
7. `public.repositorio_recursos`
8. `public.eva_visitas_eventos`
9. `public.eva_visitas_diarias`
10. `public.eva_compartidos_eventos`
11. `public.eva_compartidos_diarios`
12. Storage bucket `eva-publico`

## Calendario y Capacitaciones

`public.calendario_publico` es una vista con `security_invoker=true`; no es una segunda fuente de escritura.

La vista combina:

- `public.calendario_actividades` con `visible=true`;
- `public.capacitaciones_sesiones` con `visible=true`.

Fotografía observada:

- `calendario_actividades`: 154 filas, 152 visibles, 2 no visibles;
- `capacitaciones_sesiones`: 20 filas, 20 visibles;
- `calendario_publico`: 172 filas.

La igualdad observada `152 + 20 = 172` confirma la topología actual del flujo y será convertida en contrato explícito en la Etapa 2. No implica que el conteo 172 deba permanecer fijo.

Consumidores detectados:

- Calendario público: `crebeucayali/accesos-complementarios/recursos/calendario-supabase.js` consulta `calendario_publico`.
- Capacitación pública: `crebeucayali/capacitaciones/supabase-publico.js` consulta `capacitaciones_sesiones`.
- Administración: `crebeucayali/accesos-complementarios/admin/admin.js` y `admin/publicacion.js` operan sobre las tablas fuente.

## Noticias

- Tabla: `public.noticias_destacadas`.
- Filas observadas: 5.
- Publicadas según `visible=true` y `estado_publicacion='publicado'`: 2.
- Dependencia Storage: `imagen_url`.
- Consumidor público identificado: `crebeucayali/crebeucayali.github.io/main.js`.

## Galería

- `public.galeria_items`: 3 actividades, las 3 públicas bajo la regla observada.
- `public.galeria_item_imagenes`: 13 imágenes.
- Existe FK `galeria_item_imagenes.galeria_item_id -> galeria_items.id`.
- La página pública consulta ambas tablas desde `recursos/galeria-supabase.js`.
- Las imágenes dependen de `eva-publico/galeria/`.

## Repositorio Accesible

- Tabla: `public.repositorio_recursos`.
- Filas observadas: 21.
- Filas públicas según `visible=true` y `estado_publicacion='publicado'`: 21.
- Consumidor público: `crebeucayali/repositorio-accesible/repositorio-supabase.js`.
- Dependencia Storage: `imagen_url`.

## Storage

Bucket `eva-publico`:

- público: sí;
- límite: 5 MiB por archivo;
- MIME admitidos: WebP, JPEG y PNG;
- objetos observados: 44.

Distribución:

| Prefijo | Objetos |
|---|---:|
| `calendario/` | 4 |
| `capacitaciones/` | 3 |
| `galeria/` | 30 |
| `noticias/` | 6 |
| `repositorio/` | 1 |

La existencia de 44 objetos no implica que todos estén correctamente referenciados. La relación objeto↔registro se auditará en la Etapa 3 después de definir contratos en la Etapa 2.

## Visitas

Arquitectura inventariada:

`eva_visitas_eventos` → trigger `private.registrar_visita_eva_evento` → `eva_visitas_diarias`

- eventos observados: 0;
- agregados diarios: 57 filas;
- PK del agregado: `(fecha, modulo)`.

La tabla de eventos funciona como endpoint efímero; cero filas no se clasifica como anomalía en esta etapa.

## Compartidos

Arquitectura inventariada:

`eva_compartidos_eventos` → trigger `private.registrar_compartir_eva_evento` → `eva_compartidos_diarios`

- eventos observados: 0;
- agregados diarios: 9 filas;
- PK del agregado: `(fecha, modulo, pagina)`.

La no persistencia del evento individual forma parte de la arquitectura observada.

## RLS y exposición

Las tablas funcionales inventariadas tienen RLS habilitado. `calendario_publico` conserva `security_invoker=true`.

Se registraron los grants observados porque serán necesarios para la futura revisión de Data API, pero esta etapa no amplía permisos ni interpreta diferencias de grants como fallo de seguridad. Los asuntos de seguridad que no expliquen una inconsistencia funcional pertenecen a la fase específica de Seguridad y Permisos.

## Artefactos

- Inventario: `baselines/fase-6-etapa-1-inventario.json`
- Validador: `supabase_integrity_inventory_validate.py`
- Pruebas: `tests/test_supabase_integrity_inventory.py`
- Workflow: `.github/workflows/supabase-integrity-inventory.yml`
- Tracking: `tracking/fase-6-etapa-1.json`

## Criterios de cierre

La etapa puede cerrarse cuando:

1. estén representados los objetos funcionales de los ocho módulos priorizados;
2. Calendario y Capacitación tengan su dependencia cruzada explícita;
3. las relaciones Galería padre-hijas, eventos→agregados y tablas→Storage estén registradas;
4. se hayan identificado consumidores públicos y administrativos relevantes;
5. el artefacto sea validable sin secretos;
6. no haya existido ninguna escritura en Supabase ni modificación en EVA.

Cumplidos esos criterios, la siguiente etapa es **Etapa 2 — Contratos e invariantes por módulo**.
