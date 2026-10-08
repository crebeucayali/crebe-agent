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

## Evidencia transitoria posterior a los merges

El informe histórico de Etapa 6 permanece intacto como línea previa: 77 nodos de contraste y cuatro URLs objetivo de reflujo. Una ejecución pública posterior a los merges (`37811940130`) observó un único nodo de contraste restante en el despliegue público frente a los 77 de la línea previa.

El runner de diagnóstico conserva siempre las cuatro URLs objetivo dentro de `reflujo.detalle`, incluso cuando una URL ya no presenta desbordamiento; por tanto, la longitud de ese arreglo no puede utilizarse como contador de fallos activos.

## Separación formal de etapas

La Etapa 7 certifica que las nueve causas diagnosticadas recibieron una intervención controlada y que no se modificó nada fuera del alcance autorizado. La comprobación definitiva del despliegue público, la ausencia final de regresiones y la activación del monitoreo pertenecen a la **Etapa 8 — Verificación y monitoreo**.

Objetivo de Etapa 8:

- 0 nodos de contraste correspondientes a los hallazgos intervenidos;
- 0 desbordamientos activos a 320 px en las URLs objetivo;
- ausencia de regresiones funcionales o de accesibilidad derivadas de la corrección.

La Etapa 8 no se inicia en este cierre.
