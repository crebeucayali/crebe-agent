# Fase 6 — Etapa 5: Pruebas controladas de escritura

Estado: `ETAPA_5_COMPLETADA_PRUEBAS_CONTROLADAS`

## Objetivo

Validar de forma preventiva y reversible los mecanismos de escritura de los flujos dinámicos principales de EVA sin dejar datos de prueba persistidos ni alterar Storage.

## Método

Se ejecutó una transacción controlada en Supabase con datos marcados como `[TEST F6E5]`, todos no visibles/borrador/pendiente, y se finalizó con `ROLLBACK`.

Se probaron:

- Calendario: INSERT + UPDATE y validaciones de contenido.
- Capacitaciones: INSERT + UPDATE no visible.
- Noticias: INSERT + UPDATE en borrador.
- Galería: INSERT padre+hija y `ON DELETE CASCADE` mediante `SAVEPOINT`.
- Repositorio Accesible: INSERT + UPDATE en borrador.
- Visitas: trigger efímero, incremento global `__eva__` y por módulo.
- Compartidos: trigger efímero e incremento del agregado diario.

No se realizaron escrituras en Storage porque la línea base no presentó referencias faltantes ni un hallazgo que justificara crear o eliminar objetos reales.

## Guardrails observados

1. Los IDs son `GENERATED ALWAYS`; el esquema rechaza IDs manuales.
2. Calendario exige que `titulo` coincida con la primera línea de `contenido_lineas`.
3. En Visitas, `nueva_sesion=true` incrementa `__eva__`; `nuevo_modulo=true` incrementa el módulo concreto.

Los dos primeros intentos fueron rechazados por estas reglas antes de completar la transacción y no dejaron cambios persistidos.

## Resultado final

Todos los checks finales resultaron `true`, incluyendo:

- CRUD reversible de Calendario, Capacitaciones, Noticias, Galería y Repositorio;
- relación padre–hija y cascade de Galería;
- triggers efímeros de Visitas y Compartidos;
- ausencia de eventos persistidos.

La comprobación posterior al `ROLLBACK` confirmó 0 residuos en todos los módulos de prueba.

## Alcance y límites

Esta etapa valida la mecánica de escritura, constraints, relaciones y triggers a nivel de base de datos. No constituye una prueba E2E del recorrido completo `Panel administrativo + AAL2 + Data API + navegador`; esa validación podrá incorporarse posteriormente si se requiere.

No se modificó durablemente Supabase y no se modificó ningún repositorio EVA.
