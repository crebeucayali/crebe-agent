# Fase 8 — Etapa 6: Diagnóstico técnico de accesibilidad

Estado: `ETAPA_6_COMPLETADA_DIAGNOSTICO_ACCESIBILIDAD`

## Alcance

Esta etapa diagnostica únicamente la evidencia obtenida en la Etapa 5. No modifica los ocho repositorios EVA, no modifica Supabase y no aplica correcciones.

## Evidencia utilizada

- Workflow de diagnóstico: `37806844799`
- Artefacto: `11563855487`
- Referencia técnica: WCAG 2.2 AA
- Modo: `READ_ONLY_DIAGNOSIS`

## Contraste

Los 77 nodos confirmados se explican por seis grupos causales:

1. `.compartir-facebook`: 38 nodos. Blanco `#ffffff` sobre `#1877f2`, ratio 4.23:1.
2. `.seccion-etiqueta`: 9 nodos. `#c9f7ee` sobre blanco, ratio 1.16:1.
3. `.footer-legal-eva > a`: 9 nodos. `#1f6a5a` sobre `#17324d`, ratio 2.04:1.
4. Tarjetas BDA en construcción: 8 nodos, ratios 4.18:1 y 3.95:1.
5. Texto secundario MEA `#627d98`: 12 nodos en varios fondos, ratios observados 4.28:1, 4.08:1 y 3.24:1. Este caso requiere tratamiento contextual y no un reemplazo global del color.
6. `.noticia-enlace`: 1 nodo, `#e6f0f0` sobre `#2b867e`, ratio 3.75:1.

## Reflujo a 320 px

Las cuatro URLs observadas corresponden a tres causas técnicas:

- Contacto de Accesos Complementarios, en dos rutas: cadenas de correo largas no se fragmentan dentro de `.directorio-texto`. Corresponde al pendiente histórico `accesos-complementarios.contacto.layout.overflow`.
- Braille teoría: la grilla `.pagina-teoria` conserva el mínimo intrínseco de los items y `.tarjeta-teoria` mantiene `min-width:auto`, lo que expande la pista más allá del ancho disponible. Corresponde a `banco-digital-accesible.braille-teoria.layout.overflow`.
- Generador Braille MEA: `.contenedor-generador` mantiene `grid-template-columns:1fr 320px` sin colapso responsive. Corresponde a `materiales-educativos-accesibles.generador-braille.layout.overflow`.

## Contratos sin fallo confirmado

- `A11Y-CON-013`: conserva evidencia favorable controlada; no equivale a certificación completa de teclado.
- `A11Y-CON-027`: no aplica en el universo observado por ausencia de audio/video.
- Otros 22 contratos continúan como revisión manual o técnica y no se convierten en incumplimientos sin evidencia adicional.

## Guardrails

- Repositorios EVA modificados: no.
- Supabase modificado: no.
- Correcciones aplicadas: 0.
- Severidades de proyecto asignadas: 0.
- Etapa 7 iniciada: no.

La Etapa 7 podrá intervenir únicamente los nueve grupos causales documentados, manteniendo correcciones mínimas, trazables y con verificación de regresión.
