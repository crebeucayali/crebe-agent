# Fase 8 — Etapa 7: Corrección controlada de accesibilidad

Estado: `ETAPA_7_COMPLETADA_CORRECCION_CONTROLADA_ACCESIBILIDAD`.

## Alcance autorizado

La intervención se limita a los nueve grupos causales diagnosticados en la Etapa 6: seis de contraste y tres de reflujo. Los 22 contratos que continúan en revisión manual sin fallo confirmado no forman parte de esta corrección.

## Intervenciones EVA

Se abrieron, revisaron y fusionaron ocho PRs, uno por repositorio EVA. Se modificaron nueve archivos CSS en total. No se modificaron HTML funcional, JavaScript funcional, contenido, Supabase, autenticación, permisos ni RLS.

- Plataforma principal PR #17: contraste de Compartir y enlace de noticia.
- Accesos Complementarios PR #5: contraste de `.seccion-etiqueta` solo dentro de `main` y wrapping de correos de Contacto.
- Capacitaciones PR #3: contraste de Compartir y enlaces legales de footer.
- BDA PR #3: contraste de Compartir, estados en construcción y `min-width:0` para Braille teoría.
- MEA PR #3: contraste contextual de textos secundarios y colapso móvil del Generador Braille.
- Noti Inclusivos PR #5: contraste de Compartir en artículos.
- Repositorio Accesible PR #4: contraste de Compartir.
- DUA-3.0 PR #3: contraste de Compartir.

## Verificación de cierre

El informe histórico de Etapa 6 permanece intacto como línea previa (77 nodos de contraste y 4 URLs con overflow). Al avanzar a Etapa 7, el validador de Etapa 6 cambia a modo post-corrección y exige una nueva ejecución real de `accessibility_diagnosis.mjs` contra `main` de los ocho repositorios EVA con:

- 0 nodos `color-contrast`;
- 0 entradas de reflujo con overflow a 320 px.

La Etapa 8 no se inicia en este cierre.
