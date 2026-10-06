# Fase 6 — Integridad Supabase y flujos de datos

## Objetivo

Verificar de forma reproducible que los datos administrados en EVA mantienen integridad desde su origen hasta su visualización pública:

`Panel administrativo -> Supabase Database/Storage -> consulta publica -> componente visible`

La fase no asume que una pagina que carga correctamente tenga un flujo de datos correcto. Cada modulo debe demostrar correspondencia entre el registro fuente, sus dependencias y la salida publica.

## Alcance inicial confirmado

Proyecto Supabase: `dteimbhwtzghhsijeeld` (`crebe Project`), PostgreSQL 17.

Objetos funcionales observados:

- `public.calendario_actividades`
- `public.calendario_publico`
- `public.capacitaciones_sesiones`
- `public.noticias_destacadas`
- `public.galeria_items`
- `public.galeria_item_imagenes`
- `public.repositorio_recursos`
- `public.eva_visitas_eventos`
- `public.eva_visitas_diarias`
- `public.eva_compartidos_eventos`
- `public.eva_compartidos_diarios`
- Storage bucket publico `eva-publico`

Conteos de referencia al preparar la fase: calendario_actividades 154, calendario_publico 172, capacitaciones_sesiones 20, noticias_destacadas 5, galeria_items 3, galeria_item_imagenes 13, repositorio_recursos 21, eva_visitas_diarias 57, eva_compartidos_diarios 9. Los conteos son evidencia temporal y no se usan como valores esperados permanentes.

## Principios de control

1. **Lectura primero.** Las Etapas 1–4 no escriben datos institucionales.
2. **No confundir ausencia con fallo.** Un conjunto vacio puede ser correcto si el negocio lo permite.
3. **Trazabilidad extremo a extremo.** Todo hallazgo debe identificar modulo, tabla/vista/bucket, campo o relacion, consulta consumidora y pagina/componente de salida.
4. **Una causa, un hallazgo.** No multiplicar un mismo defecto por cada fila o pagina afectada.
5. **No usar produccion para pruebas destructivas.** INSERT/UPDATE/DELETE de prueba solo en entorno aislado o mediante transaccion reversible expresamente diseñada.
6. **No tocar RLS para resolver un fallo funcional.** Un error de permisos pasa primero a diagnostico; nunca se corrige ampliando acceso sin justificar el modelo de autorizacion.
7. **Storage y base de datos se verifican juntos.** Una URL guardada sin objeto real, o un objeto sin registro que lo referencie, cuenta como inconsistencia.
8. **Publicacion visible ≠ existencia en tabla.** Deben verificarse filtros como `visible`, estado, fechas, orden y vistas publicas.
9. **No exponer secretos.** El agente nunca almacena `service_role`, claves secretas ni tokens en artefactos o repositorios.
10. **Correccion separada de deteccion.** Ningun hallazgo autoriza cambios automaticamente.

## Criterios de integridad

### A. Integridad estructural
- tablas, vistas, columnas y relaciones esperadas existen;
- tipos y nulabilidad son compatibles con el codigo consumidor;
- claves y relaciones no generan registros huerfanos;
- vistas publicas representan correctamente su fuente.

### B. Integridad de publicacion
- un registro publicable cumple las condiciones que usa la web publica;
- un registro archivado/no visible no aparece publicamente;
- los campos requeridos para renderizar no quedan nulos o vacios de forma invalida;
- las fechas, estados, categorias y niveles conservan valores validos.

### C. Integridad Database ↔ Storage
- toda imagen/archivo referenciado existe donde corresponde;
- no hay referencias a objetos inexistentes;
- se distinguen objetos compartidos de objetos huerfanos antes de cualquier limpieza;
- MIME, extension y bucket coinciden con el uso previsto.

### D. Integridad de agregados
- visitas y compartidos no presentan divergencias inexplicables entre eventos y agregados;
- los contadores se consideran telemetria y no se corrigen mediante inserciones de prueba en produccion.

### E. Integridad de flujo
Para cada modulo se define una cadena verificable:

`accion esperada -> objeto fuente -> regla de publicacion -> consulta cliente -> salida publica`

## Prioridad de modulos dentro de la fase

1. Calendario.
2. Capacitaciones.
3. Noticias destacadas.
4. Galeria e imagenes.
5. Repositorio Accesible.
6. Storage `eva-publico` y referencias cruzadas.
7. Visitas.
8. Compartidos.

Calendario y Capacitaciones se revisan primero porque existe dependencia funcional entre ambos y una vista publica consolidada.

## Etapas

### Etapa 1 — Inventario de datos y dependencias

Levantar un mapa real de:
- tablas, vistas, columnas, PK/FK, indices relevantes y triggers;
- buckets y objetos Storage utilizados por EVA;
- codigo EVA que lee/escribe cada objeto;
- modulo y pagina publica consumidora.

Salida esperada:
`objeto -> productor -> regla -> consumidor -> pagina`

Estado de cierre: `ETAPA_1_COMPLETADA_INVENTARIO_DATOS`

### Etapa 2 — Contratos e invariantes por modulo

Definir para cada flujo qué significa "correcto" sin modificar datos.

Ejemplos:
- una capacitacion visible debe aparecer en su pagina y, si aplica, en Calendario;
- una actividad archivada no debe aparecer en la vista publica;
- una galeria con imagen debe tener referencia valida en `galeria_item_imagenes` y objeto accesible;
- un recurso publicado debe conservar URL/categoria/tipo suficientes para renderizar.

Estado de cierre: `ETAPA_2_COMPLETADA_CONTRATOS_INTEGRIDAD`

### Etapa 3 — Auditoria de integridad de solo lectura

Ejecutar SQL SELECT y comprobaciones HTTP/Storage no destructivas.

Estados permitidos:
- `INTEGRO`
- `INCONSISTENCIA_CONFIRMADA`
- `REQUIERE_VERIFICACION_CONTROLADA`
- `BLOQUEADO_POR_PERMISOS_O_DEPENDENCIA`
- `NO_APLICA`

No realizar INSERT/UPDATE/DELETE.

Estado de cierre: `ETAPA_3_COMPLETADA_LINEA_BASE_INTEGRIDAD`

### Etapa 4 — Priorizacion y agrupacion causal

Agrupar inconsistencias por causa real, no por número de registros afectados.

Severidad:
- `CRITICO`: perdida/corrupcion de datos, exposicion indebida o flujo administrativo esencial inutilizable;
- `ALTO`: contenido institucional correcto en BD pero ausente/incorrecto publicamente, o inconsistencia repetida entre modulos;
- `MEDIO`: inconsistencia localizada con alternativa funcional;
- `BAJO`: deuda tecnica sin efecto inmediato sobre el usuario.

Estado de cierre: `ETAPA_4_COMPLETADA_PRIORIZACION_INTEGRIDAD`

### Etapa 5 — Pruebas controladas de escritura

Solo para flujos que no puedan certificarse por lectura.

Orden de preferencia:
1. entorno/branch Supabase aislado;
2. transaccion de prueba con rollback y datos identificables;
3. produccion solo cuando no exista alternativa, con autorizacion explicita, fixture minimo y limpieza verificada.

Se prueban, cuando corresponda: crear, editar, archivar/publicar, eliminar y subir/reemplazar imagen.

Estado de cierre: `ETAPA_5_COMPLETADA_PRUEBAS_CONTROLADAS`

### Etapa 6 — Diagnostico tecnico

Para cada inconsistencia confirmada registrar:
- causa raiz;
- objeto Supabase implicado;
- codigo consumidor/productor;
- RLS/politica/funcion involucrada si aplica;
- alcance de datos afectados;
- correccion minima propuesta;
- riesgo de regresion.

Estado de cierre: `ETAPA_6_COMPLETADA_DIAGNOSTICO_INTEGRIDAD`

### Etapa 7 — Correccion controlada

Aplicar una causa por intervencion, con migracion o PR separado cuando corresponda.

Estado de cada correccion:
`CORREGIDO_PENDIENTE_VERIFICACION`

No mezclar correcciones funcionales, permisos y rediseños de datos en una sola intervencion.

Estado de cierre: `ETAPA_7_COMPLETADA_CORRECCION_CONTROLADA`

### Etapa 8 — Verificacion y monitoreo

Repetir el contrato afectado despues del cambio y añadir centinelas de integridad al monitoreo permanente del agente.

Estados:
- `CORREGIDO_VERIFICADO`
- `FALLO_PERSISTENTE`
- `REGRESION_DETECTADA`

Estado permanente: `MONITOREO_INTEGRIDAD_ACTIVO`

## Regla de avance

No se inicia una etapa de correccion por la sola existencia de una anomalia. La secuencia obligatoria es:

`inventario -> contrato -> evidencia -> priorizacion -> prueba controlada si hace falta -> diagnostico -> correccion -> verificacion`

## Condicion especial de Supabase 2026

La fase debe verificar explicitamente grants/Data API de las tablas consumidas por el frontend. Supabase anunció que el 30 de octubre de 2026 se aplicará a proyectos existentes el cambio por el cual las tablas nuevas dejan de exponerse automaticamente a Data/GraphQL API. Esta verificacion debe hacerse sin relajar RLS ni otorgar acceso mas amplio del requerido.

## Fuera de alcance inicial

- rediseño completo de autenticacion;
- endurecimiento general de contraseñas;
- auditoria integral de secretos;
- cambios de seguridad no necesarios para explicar un fallo de integridad;
- limpieza masiva de Storage;
- eliminacion de registros historicos.

Los hallazgos puramente de seguridad se derivan a la futura fase de Seguridad y Permisos, aunque puedan documentarse como dependencia.
