# Mapa Web - Etapa 4: validación controlada del verificador

Estado: VALIDACION_CONTROLADA_COMPLETADA

## Alcance

Esta etapa valida el verificador de solo lectura implementado en la Etapa 3 contra el estado real de los ocho repositorios EVA, sin modificar `mapa-web.html`, sin alterar repositorios productivos y sin escribir en Supabase.

La validación utiliza la línea base fijada en `tracking/mapa-web-baseline.json`, los estados actuales de `main` y la inspección de las rutas públicas relevantes.

## Resultado de estabilidad de la línea base

Los ocho repositorios supervisados conservan en `main` los mismos commits fijados en la línea base de la Etapa 3. Por tanto, durante esta validación no existen páginas HTML creadas después de la línea base que deban clasificarse por defecto como `PENDIENTE_CONFIRMACION`.

Repositorios supervisados:

- `crebeucayali/crebeucayali.github.io`
- `crebeucayali/accesos-complementarios`
- `crebeucayali/capacitaciones`
- `crebeucayali/banco-digital-accesible`
- `crebeucayali/materiales-educativos-accesibles`
- `crebeucayali/noti-inclusivos`
- `crebeucayali/repositorio-accesible`
- `crebeucayali/DUA-3.0`

No se detectaron marcas `data-mapa-web` en los repositorios actuales. La clasificación de las páginas existentes sigue dependiendo de `LEGADO_APROBADO`, del Mapa Web publicado y de las exclusiones técnicas.

## Exclusiones confirmadas

Se mantienen fuera del Mapa Web:

- `/pruebas/buscador-accesible/`: ruta histórica/compatibilidad bajo `pruebas`, redirige a `/buscar/` y declara `noindex`.
- `/pruebas/tarjetas-educativas/`: ruta experimental bajo `pruebas`.
- `/pruebas/generador-por-pasos/`: referencia obsoleta de prototipo que ya no existe como ruta actual.
- cualquier ruta futura bajo `/pruebas/**`, salvo revisión editorial expresa.

Estas rutas no deben generar propuestas de publicación.

## Candidatos válidos ausentes del Mapa Web

La validación confirmó los siguientes accesos actuales como contenido público sustantivo existente en la línea base y ausente del Mapa Web canónico:

### INICIO

- `https://crebeucayali.github.io/buscar/` - Buscador de EVA.

### CAP

- `https://crebeucayali.github.io/capacitaciones/primera-jornada.html`
- `https://crebeucayali.github.io/capacitaciones/segunda-jornada.html`

### BDA

- `https://crebeucayali.github.io/banco-digital-accesible/creditos.html` - Créditos y condiciones de uso generales del BDA.

### MEA

- `https://crebeucayali.github.io/materiales-educativos-accesibles/apoyos-lsp/generador-lsp.html` - Generador que consulta señas completas cuando existen y utiliza deletreo cuando corresponde. Es funcionalmente distinto del generador dactilológico ubicado en `/generador-lsp/`.

### DUA

El módulo DUA completo está ausente como grupo del Mapa Web, aunque forma parte del ecosistema publicado. Deben considerarse candidatos:

- `https://crebeucayali.github.io/DUA-3.0/`
- `https://crebeucayali.github.io/DUA-3.0/evolucion.html`
- `https://crebeucayali.github.io/DUA-3.0/recursos.html`

Total de candidatos válidos confirmados para una futura actualización controlada: **8**.

## Falsos positivos de compatibilidad detectados

La validación identificó dos páginas HTML existentes que el criterio simple de `LEGADO_APROBADO` podría interpretar como publicables, pero que no deben convertirse en entradas independientes del mapa porque solo conservan compatibilidad con rutas antiguas:

1. `accesos-complementarios/paginas/mapa-web.html`
   - declara `noindex,follow`;
   - redirige inmediatamente a `../mapa-web.html`;
   - declara como canónica la ruta principal `mapa-web.html`.

2. `accesos-complementarios/recursos/contacto.html`
   - redirige inmediatamente a `../paginas/contacto.html`;
   - declara como canónica la página institucional de contacto.

Estado de ambos: `NO_PUBLICAR_EN_MAPA_COMPATIBILIDAD` para fines de validación. No se introduce todavía un nuevo estado permanente en el verificador; la Etapa 5 deberá resolver técnicamente esta exclusión sin alterar las páginas productivas.

## Validación de reglas

Casos comprobados:

- ruta bajo `/pruebas/` -> exclusión correcta;
- ruta pública existente antes de la línea base y ya registrada -> debe permanecer `YA_REGISTRADO`;
- ruta pública existente antes de la línea base y no registrada -> candidata `PUBLICAR_EN_MAPA`;
- ruta futura sin marca -> debe quedar `PENDIENTE_CONFIRMACION`;
- `data-mapa-web="no-publicar"` -> debe bloquear publicación;
- `data-mapa-web="publicar"` -> solo habilita candidatura, no escritura automática;
- redirección de compatibilidad hacia otra ruta canónica -> no debe publicarse como entrada independiente.

## Hallazgos que no se corrigen en esta etapa

- No se añade DUA al Mapa Web.
- No se incorpora el Buscador de EVA.
- No se añaden las jornadas de CAP.
- No se añade Créditos de BDA.
- No se añade el segundo generador LSP de MEA.
- No se modifica la lógica del verificador para detectar automáticamente redirecciones de compatibilidad.
- No se insertan marcas `data-mapa-web` en páginas actuales.

## Criterio de cierre

La Etapa 4 queda cerrada porque:

- la línea base se mantiene estable en los ocho repositorios;
- las exclusiones de `/pruebas/` fueron verificadas;
- no existen nuevas páginas posteriores a la línea base que requieran confirmación;
- se identificaron ocho candidatos públicos válidos ausentes del mapa;
- se identificaron dos falsos positivos de compatibilidad que deben excluirse antes de automatizar propuestas;
- no se modificó ningún repositorio EVA productivo.

Estado final: `VALIDACION_CONTROLADA_COMPLETADA_CON_AJUSTES_PREVIOS_A_PUBLICACION`.
