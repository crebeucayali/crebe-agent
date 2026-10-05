# Fase 5, Etapa 4: clasificación y priorización de hallazgos funcionales

## Objetivo

Convertir los casos `FALLO_CONFIRMADO` de la Etapa 3 en hallazgos causales únicos, evitando tratar referencias repetidas al mismo destino como problemas distintos.

## Criterio de clasificación

La Etapa 4 considera alcance, repetición, cantidad de páginas afectadas, cantidad de repositorios afectados y tipo de función comprometida.

Se utilizan las siguientes severidades:

- `CRITICO`: caída global, seguridad, autenticación, pérdida/corrupción de datos o función institucional esencial sin alternativa.
- `ALTO`: fallo reproducible que afecta navegación o función relevante en varias páginas o repositorios.
- `MEDIO`: fallo reproducible, visible y localizado, sin evidencia de afectación sistémica.
- `BAJO`: anomalía menor que no impide una función relevante.

La prioridad operativa derivada es `P0_CRITICA`, `P1_ALTA`, `P2_MEDIA` o `P3_BAJA`.

## Fuente

La clasificación consume el artefacto validado de la Etapa 3 (`artifact_id 11322878003`, workflow `37256684229`). No vuelve a recorrer los ocho repositorios EVA y no ejecuta nuevas pruebas contra producción.

## Resultado esperado

Los 21 casos confirmados deben quedar agrupados por destino/cause key. Cada hallazgo conserva:

- ID estable;
- destino causante;
- evidencia HTTP;
- cantidad de casos;
- repositorios y páginas afectadas;
- severidad;
- prioridad;
- justificación;
- estado `PRIORIZADO_PENDIENTE_DIAGNOSTICO`.

## Límites

Esta etapa no modifica EVA, no corrige enlaces, no crea PR en los repositorios EVA y no convierte los 280 casos manuales ni los 133 bloqueados en fallos.

## Criterio de cierre

1. Los 21 casos `FALLO_CONFIRMADO` quedan representados sin pérdida ni duplicación causal.
2. Los hallazgos únicos tienen severidad y prioridad justificadas.
3. La suma de casos agrupados es exactamente 21.
4. Las pruebas automatizadas y el workflow terminan correctamente.
5. No se modifica ninguno de los ocho repositorios EVA.
6. La Etapa 5 permanece sin iniciar.
