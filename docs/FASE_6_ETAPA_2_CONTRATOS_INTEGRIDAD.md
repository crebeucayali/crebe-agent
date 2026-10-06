# Fase 6 · Etapa 2 — Contratos e invariantes por módulo

## Objetivo

Transformar el inventario de la Etapa 1 en reglas objetivas que permitan decidir, en la Etapa 3, si cada flujo está íntegro o presenta una inconsistencia.

Esta etapa **no ejecuta correcciones**, no modifica Supabase y no cambia EVA.

## Principios

1. Los conteos de la Etapa 1 son una fotografía, no contratos permanentes.
2. Los contratos describen relaciones y condiciones que deben mantenerse aunque cambie la cantidad de registros.
3. La Etapa 3 será de solo lectura.
4. Un fallo se agrupará por causa técnica, no por cantidad de filas afectadas.
5. Los hallazgos de seguridad que no expliquen directamente una inconsistencia funcional se derivarán a la fase de Seguridad y permisos.

## Contratos definidos

Se definieron contratos para ocho módulos:

1. Calendario.
2. Capacitaciones.
3. Noticias.
4. Galería.
5. Repositorio Accesible.
6. Storage `eva-publico`.
7. Visitas.
8. Compartidos.

El archivo canónico es:

`contracts/fase-6-etapa-2-integridad.json`

### Calendario

La regla central es dinámica:

`calendario_publico = actividades visibles + capacitaciones visibles`

La vista debe conservar `security_invoker=true`, diferenciar correctamente las fuentes y no duplicar físicamente las capacitaciones.

También se controlarán estados permitidos, unicidad `(fecha, origen, orden)`, contenido no vacío, imágenes permitidas y texto alternativo cuando exista imagen.

### Capacitaciones

Se exige unicidad `(jornada, numero_sesion)`, proyección única al Calendario para cada sesión visible, textos obligatorios y coherencia entre estado `disponible` y existencia de recursos.

### Noticias

`visible` debe ser equivalente a `estado_publicacion='publicado'`; el público anónimo solo debe leer contenido publicado y visible. Las referencias a Storage deben existir.

### Galería

Se exige:

- coherencia publicación/visibilidad;
- autorización explícita para elementos visibles;
- relación padre-hijas sin huérfanos;
- orden de imágenes único por actividad, de 1 a 8;
- lectura pública únicamente de actividades publicadas, visibles y autorizadas;
- referencias de imagen válidas.

### Repositorio Accesible

`visible` debe equivaler a `estado_publicacion='publicado'`; las categorías permanecen limitadas a las tres institucionales y las referencias Storage deben existir.

### Storage

El bucket `eva-publico` debe continuar público porque EVA consume URLs públicas actuales. Su contrato observado incluye límite de 5 MiB y MIME `image/webp`, `image/jpeg`, `image/png`.

Un objeto sin referencia no se elimina automáticamente: solo se reporta para revisión.

### Visitas y Compartidos

Las tablas `*_eventos` son endpoints efímeros. El evento válido dispara un trigger, incrementa el agregado diario y no debe permanecer como historial ordinario.

Los agregados deben mantener claves únicas, dimensiones válidas y valores no negativos. El público puede insertar eventos válidos, pero no debe tener lectura directa de los agregados históricos.

## Exposición Data API

La Etapa 3 comprobará que los objetos consumidos por el frontend mantengan la exposición mínima necesaria mediante grants y RLS. Esta comprobación también sirve como preparación para el cambio anunciado por Supabase para el 30 de octubre de 2026.

La Etapa 2 no amplía ni reduce grants.

## Validación automática

Se añadieron:

- `supabase_integrity_contracts_validate.py`
- `tests/test_supabase_integrity_contracts.py`
- `.github/workflows/supabase-integrity-contracts.yml`

El validador exige:

- exactamente los ocho módulos esperados y en orden de prioridad;
- IDs de contrato únicos;
- tipos de verificación controlados;
- contratos críticos presentes;
- escritura deshabilitada;
- corrección automática deshabilitada.

## Criterio de cierre

La etapa puede cerrarse como:

`ETAPA_2_COMPLETADA_CONTRATOS_INTEGRIDAD`

cuando el contrato canónico pase sus pruebas y quede trazable desde el inventario de la Etapa 1.

La Etapa 3 no se inicia automáticamente.
