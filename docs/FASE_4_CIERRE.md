# Fase 4 — Cierre

## Estado final

COMPLETADA_CON_PENDIENTES_DOCUMENTADOS

Fecha de cierre: 2026-10-04T20:35:08-05:00 (America/Lima).

Fuente del inventario y de las evidencias: `tracking/fase-4.json`, leído en main de crebe-agent en el commit `97590d6430694d167b1c4c70bd7b9065b8b72758`. Este cierre se propone en la rama `docs/cierre-fase-4`; su incorporación a main requiere aprobación y merge del PR.

El inventario real contiene 18 hallazgos: 12 CORREGIDO_VERIFICADO y 6 PENDIENTE_DE_DIAGNOSTICO. Los pendientes son registros agrupados: tres de overflow y tres de recursos 404. Estos últimos documentan trece imágenes (dos de BDA, una de Noti Inclusivos y diez de Repositorio Accesible), no trece hallazgos independientes.

El cierre reconoce deuda técnica. No declara los repositorios libres de hallazgos, 100 % corregidos ni sin pendientes.

## Alcance

La Fase 4 estuvo orientada a correcciones controladas, ramas independientes, PR verificables, validación antes/después y preservación de cambios previos, sin auto-merge. Se completaron las correcciones prioritarias, las siete normalizaciones tipográficas y los desbordamientos principales seleccionados. Los hallazgos secundarios restantes se conservan documentados; no se continúa una cadena indefinida de correcciones menores.

Este cierre modifica únicamente crebe-agent. No cambia páginas publicadas, código, ramas ni PR de los ocho repositorios EVA: crebeucayali.github.io, accesos-complementarios, capacitaciones, banco-digital-accesible, materiales-educativos-accesibles, noti-inclusivos, repositorio-accesible y DUA-3.0. No se inicia Fase 5.

## Correcciones cerradas

Las doce filas siguientes proceden de los registros CORREGIDO_VERIFICADO del tracking. No se modifican retrospectivamente sus evidencias, estados, PR, hashes ni mediciones.

| Repositorio | Hallazgo | PR | Commit de corrección | Commit de merge | Estado final |
|---|---|---|---|---|---|
| crebeucayali/repositorio-accesible | Desbordamiento horizontal móvil causado por .tarjeta-recurso:before | [#2](https://github.com/crebeucayali/repositorio-accesible/pull/2) | `d58ecf44951363025287f31b37645bc7c895d177` | `55d091f9ed0d09f5e2604d18b718d76bfafe0a0d` | CORREGIDO_VERIFICADO |
| crebeucayali/DUA-3.0 | Etiqueta visible Compartir en Facebook en tres páginas de DUA-3.0 | [#1](https://github.com/crebeucayali/DUA-3.0/pull/1) | `969330db63f50a42c5c2269ff88392b7b45dd5ff` | `903b338b509c4dc368986a3fb8a741a44cee1e85` | CORREGIDO_VERIFICADO |
| crebeucayali/accesos-complementarios | Overflow horizontal del contenido de política de cookies a 320 px | [#2](https://github.com/crebeucayali/accesos-complementarios/pull/2) | `eb01ee9bd2f9ee144480bff6c394bc215e9e3757` | `780114cf6d5500e5c9b92cf94b07221db4deae0b` | CORREGIDO_VERIFICADO |
| crebeucayali/accesos-complementarios | Overflow horizontal del contenido de política de privacidad a 320 y 360 px | [#3](https://github.com/crebeucayali/accesos-complementarios/pull/3) | `4cdb96284736c8054766c431bf7b40e2263755d6` | `3648768ecc3b9933339adf6589de6df1c3b16a99` | CORREGIDO_VERIFICADO |
| crebeucayali/accesos-complementarios | Inconsistencia tipográfica de enlaces de navegación | [#1](https://github.com/crebeucayali/accesos-complementarios/pull/1) | `040075828377bb7c9c11142d6fc43f847644881a` | `ad2997def265bc219ec8729fa26b58488198258a` | CORREGIDO_VERIFICADO |
| crebeucayali/banco-digital-accesible | Inconsistencia tipográfica de navegación en trece páginas | [#2](https://github.com/crebeucayali/banco-digital-accesible/pull/2) | `2002f7dfea6b98c38a0e977faf283bd6870ddbff` | `d4967f60e1e5ef04ec4bbf6b543ca27eb853e71b` | CORREGIDO_VERIFICADO |
| crebeucayali/noti-inclusivos | Inconsistencia tipográfica de navegación en nueve páginas | [#2](https://github.com/crebeucayali/noti-inclusivos/pull/2) | `78d6e8efcfbc05dee8aa607415f2a27214c7c631` | `96f58b6fdd456388e861f856534dfed199a75551` | CORREGIDO_VERIFICADO |
| crebeucayali/capacitaciones | Inconsistencia tipográfica de navegación en tres páginas | [#2](https://github.com/crebeucayali/capacitaciones/pull/2) | `2bbf856fe8343b1a6383f8b9a7bebbfa538081c9` | `3b8dbba6c62250b88677732fd89e4184131d82ed` | CORREGIDO_VERIFICADO |
| crebeucayali/materiales-educativos-accesibles | Inconsistencia tipográfica de navegación en once páginas | [#2](https://github.com/crebeucayali/materiales-educativos-accesibles/pull/2) | `3667527d108eafdf21b7a75ab44d451172cd07cc` | `a143e6d2d70d948fa9088ac030e4f69d7a1061f1` | CORREGIDO_VERIFICADO |
| crebeucayali/repositorio-accesible | Inconsistencia tipográfica de navegación | [#3](https://github.com/crebeucayali/repositorio-accesible/pull/3) | `121677db73fae6894b71bcfd17ea9c7eb3a6d3d1` | `d0424d850c5ca67638c556995f21b1ef654a010c` | CORREGIDO_VERIFICADO |
| crebeucayali/DUA-3.0 | Inconsistencia tipográfica de navegación institucional en tres páginas | [#2](https://github.com/crebeucayali/DUA-3.0/pull/2) | `1f836ddf0baa9f6b4135e4023c9a78efbdcdd353` | `42bb2ecac871f64a532fb8da83a0968280b7dafc` | CORREGIDO_VERIFICADO |
| crebeucayali/accesos-complementarios | Overflow independiente de los bloques del footer a 320 px con texto Muy grande | [#4](https://github.com/crebeucayali/accesos-complementarios/pull/4) | `729e402c5a4c6c9379cef2a334a7d5ba7d92f124` | `69b456a1a7c2d783358f90d74ce8144c508c3ff4` | CORREGIDO_VERIFICADO |

## Bloque tipográfico

Los siete hallazgos tipográficos quedaron CORREGIDO_VERIFICADO: Accesos Complementarios, Banco Digital Accesible, Noti Inclusivos, Capacitaciones, Materiales Educativos Accesibles, Repositorio Accesible y DUA-3.0.

Referencia final registrada:

- Móvil: 14 px / font-weight 600.
- Escritorio: 15 px / font-weight 600.

Cada registro conserva sus páginas, anchos, pruebas de aumento de texto, cascada y variaciones naturales autorizadas. Este cierre documental no repite auditorías ni aplica cambios tipográficos.

## Otras correcciones cerradas

Las cinco correcciones no tipográficas también permanecen CORREGIDO_VERIFICADO:

- Repositorio Accesible, PR #2: overflow móvil de 10 a 0 px; preservación de `.tarjeta-recurso:before` con `right:0`.
- DUA-3.0, PR #1: tres etiquetas visibles "Compartir en Facebook" sustituidas por "Compartir"; atributos y lógica conservados.
- Accesos Complementarios, PR #2: códigos largos de Política de cookies, de 18 a 0 px a 320 px; seis anchos y nueve estados de aumento de texto registrados.
- Accesos Complementarios, PR #3: correo de Política de privacidad, de 42 a 0 px a 320 px y de 2 a 0 px a 360 px; seis anchos y nueve estados registrados.
- Accesos Complementarios, PR #4: correo del footer compartido en dos CSS, de aproximadamente 28/26 a 0 px; 13 páginas y 234 escenarios, 39 aumentos naturales de altura, 195 sin variación y 18 controles de Mapa web. Contacto conserva su overflow independiente.

Los commits y PR de estas correcciones se encuentran en la tabla anterior. Sus hallazgos independientes se mantienen separados.

## Pendientes

Los seis registros siguientes se conservan en su estado original PENDIENTE_DE_DIAGNOSTICO. Solo se añaden metadatos de cierre: `categoria_cierre: BACKLOG_FASE_4`, `prioridad_cierre: DIFERIDA_SUJETA_A_REAPERTURA` y `motivo_backlog`. La prioridad es una decisión administrativa de este cierre, no una medición histórica ni una orden de intervención.

| ID | Repositorio | Tipo | Estado | Evidencia resumida | Prioridad actual de cierre | Motivo para mantenerlo en backlog |
|---|---|---|---|---|---|---|
| `banco-digital-accesible.braille-teoria.layout.overflow` | crebeucayali/banco-digital-accesible | Overflow | PENDIENTE_DE_DIAGNOSTICO | braille/teoria.html: 51 px a 320 px y 11 px a 360 px. | DIFERIDA_SUJETA_A_REAPERTURA | Problema de contenido móvil separado de la normalización tipográfica; requiere diagnóstico propio antes de cualquier cambio. |
| `banco-digital-accesible.lsp.assets.404` | crebeucayali/banco-digital-accesible | Imágenes / recursos 404 | PENDIENTE_DE_DIAGNOSTICO | lsp/index.html solicita con.png y fresco.png: HTTP 404; ambos ausentes de main. | DIFERIDA_SUJETA_A_REAPERTURA | Dos recursos ausentes; debe determinarse el archivo o referencia correcta y la relevancia visible antes de corregir. |
| `noti-inclusivos.assets.sindrome-down.404` | crebeucayali/noti-inclusivos | Imágenes / recursos 404 | PENDIENTE_DE_DIAGNOSTICO | assets/img/sindrome-down-ciencia-bioetica.jpeg: HTTP 404, ausente de main; solicitado por portada, índice de artículos y artículo de síndrome de Down. | DIFERIDA_SUJETA_A_REAPERTURA | Recurso ausente en tres páginas; falta determinar si corresponde incorporar el archivo o ajustar su referencia. |
| `materiales-educativos-accesibles.generador-braille.layout.overflow` | crebeucayali/materiales-educativos-accesibles | Overflow | PENDIENTE_DE_DIAGNOSTICO | generador/generador.html: 255/215/185/161 px a 320/360/390/414 px; 0 px a 768/1440 px. A 390 px, Grande/Muy grande = 200/215 px. | DIFERIDA_SUJETA_A_REAPERTURA | Problema de distribución del generador, independiente de la navegación; requiere diagnóstico y validación funcional propios. |
| `repositorio-accesible.assets.materiales-elaborados.404` | crebeucayali/repositorio-accesible | Imágenes / recursos 404 | PENDIENTE_DE_DIAGNOSTICO | index.html: diez solicitudes WebP en assets/imagenes/materiales-elaborados/, todas HTTP 404 y sin archivo correspondiente en main. | DIFERIDA_SUJETA_A_REAPERTURA | Diez recursos agrupados por causa observable común; debe determinarse el origen de las ausencias y su impacto visible. |
| `accesos-complementarios.contacto.layout.overflow` | crebeucayali/accesos-complementarios | Overflow | PENDIENTE_DE_DIAGNOSTICO | paginas/contacto.html: a 320 px, Normal/Grande/Muy grande = 67/109/151 px; footer corregido = 0 px. El registro conserva causa preliminar pendiente. | DIFERIDA_SUJETA_A_REAPERTURA | Desbordamiento independiente del footer, contenido en Contacto. Se conserva pendiente y no se inicia otra corrección en este cierre. |

No hay otros registros pendientes en el tracking leído. El inventario se limita a ese archivo; no afirma que describa toda anomalía posible de EVA. Las evidencias resumidas conservan los valores históricos y no sustituyen los detalles de cada registro.

## Criterio de reapertura

Un hallazgo de BACKLOG_FASE_4 solo debe retomarse si cumple al menos una de estas condiciones:

- Rompe una función.
- Afecta el uso normal.
- Genera un recurso visible faltante relevante.
- Produce una barrera de accesibilidad significativa.
- Provoca una regresión.
- Es reportado por usuarios.
- Pasa a ser prioritario por una nueva necesidad institucional.

No se reabre un hallazgo únicamente porque exista una anomalía marginal reproducible. Antes de intervenir se debe establecer su impacto, alcance y prioridad y contar con autorización para una corrección controlada. La clasificación como backlog no elimina evidencias ni equivale a un estado corregido.

## Validación del cierre

El documento y `tracking/phases.json` utilizan los recuentos e identificadores reales de `tracking/fase-4.json`. Se validan todos los JSON y se ejecuta la suite existente con `python -m unittest discover -s tests -v`. Se comprueba que los doce registros corregidos permanecen idénticos, que los seis pendientes conservan todos sus campos históricos y que el diff se limita a los tres archivos de cierre en crebe-agent.

Resultado de la validación: ocho JSON sintácticamente correctos; diez pruebas existentes aprobadas. La comparación estructural confirma doce registros corregidos sin cambios y seis pendientes con solo los tres metadatos de cierre añadidos. Las tablas del documento coinciden con los PR, hashes, estados e identificadores reales del tracking.

## Conclusión

Los repositorios continúan operativos según las verificaciones registradas, con las limitaciones y pendientes descritos. Este cierre no constituye una nueva auditoría funcional de los ocho repositorios ni una certificación integral de accesibilidad.

La Fase 4 no pretende eliminar toda anomalía marginal. Los pendientes quedan documentados para mantenimiento posterior, sujetos al criterio de reapertura. No se inicia Fase 5 como parte de este cierre.
