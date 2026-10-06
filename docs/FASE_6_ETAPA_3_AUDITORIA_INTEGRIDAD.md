# Fase 6 · Etapa 3 — Auditoría de integridad de solo lectura

## Objetivo

Ejecutar los 42 contratos definidos en la Etapa 2 contra el estado real de Supabase y producir una línea base trazable sin modificar datos, esquema, RLS, grants ni Storage.

## Resultado

Estado de cierre: `ETAPA_3_COMPLETADA_LINEA_BASE_INTEGRIDAD`.

- Contratos ejecutados: 42.
- `INTEGRO`: 42.
- `INCONSISTENCIA_CONFIRMADA`: 0.
- `REQUIERE_VERIFICACION_CONTROLADA`: 0.
- `BLOQUEADO_POR_PERMISOS_O_DEPENDENCIA`: 0.
- `NO_APLICA`: 0.

## Evidencia destacada

### Calendario y Capacitaciones

La vista `public.calendario_publico` continúa como `security_invoker=true`.

La relación observada es dinámica y consistente:

- actividades visibles: 152;
- capacitaciones visibles: 20;
- filas de la vista: 172;
- capacitaciones proyectadas: 20/20.

La primera prueba de `CAP-002` produjo un falso negativo por extraer el identificador desde una posición incorrecta de `capacitacion-N`. Se corrigió la prueba antes de clasificar el contrato. No hubo cambio de datos.

### Publicación y RLS

Noticias, Galería y Repositorio mantienen coherencia entre estado de publicación y visibilidad. Las políticas públicas observadas limitan lectura a los registros que corresponden al consumo público de EVA.

### Storage

Bucket `eva-publico`:

- `public=true`;
- límite 5 MiB;
- MIME permitidos: `image/webp`, `image/jpeg`, `image/png`.

Referencias persistidas detectadas hacia Storage: 23. Corresponden a 20 objetos únicos. Faltantes: 0.

Existen 24 objetos del bucket que no aparecen referenciados por las columnas funcionales auditadas. Se registran como `candidatos_revision` y no como inconsistencia confirmada. La Etapa 3 no elimina objetos.

### Visitas y Compartidos

Los triggers privados de los endpoints efímeros están presentes. Las tablas `eva_visitas_eventos` y `eva_compartidos_eventos` mantienen 0 eventos persistidos, mientras los agregados diarios conservan sus restricciones y acceso administrativo protegido.

## Dependencia de Seguridad

Se observaron grants de tabla potencialmente más amplios de lo estrictamente necesario en `public.galeria_item_imagenes`. RLS continúa controlando el acceso efectivo y no se observó una ruptura funcional de integridad. Esta observación se deriva a la futura fase `Seguridad y permisos`; no se modifica ningún grant en Fase 6.

## Garantías

- No se ejecutó `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE` ni DDL.
- No se modificó Supabase.
- No se modificó ninguno de los ocho repositorios EVA.
- No se ejecutó corrección automática.
- Los conteos observados son evidencia temporal, no contratos fijos.

## Siguiente etapa

Etapa 4 — Priorización y agrupación causal. Al no existir inconsistencias confirmadas, deberá registrar una línea base limpia y conservar únicamente dependencias/candidatos de revisión sin fabricar hallazgos.
