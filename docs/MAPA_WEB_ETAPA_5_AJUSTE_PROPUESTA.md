# Mapa Web - Etapa 5: ajuste del verificador y propuesta controlada

Estado: AJUSTE_VERIFICADOR_Y_PROPUESTA_COMPLETADOS

## Alcance

Esta etapa aplica exclusivamente los hallazgos validados en la Etapa 4 dentro de `crebe-agent`.

No modifica `crebeucayali/accesos-complementarios/mapa-web.html`, no cambia ningún repositorio EVA productivo y no escribe en Supabase.

## Ajuste aplicado al verificador

El verificador de solo lectura ahora reconoce redirecciones inequívocas de compatibilidad.

Una página se considera ruta de compatibilidad cuando:

1. contiene `meta http-equiv="refresh"` con un destino;
2. declara `link rel="canonical"`;
3. ambos destinos resuelven a la misma URL;
4. esa URL es distinta de la ruta actual.

Cuando se cumplen las cuatro condiciones, la página queda clasificada como `NO_PUBLICAR_EN_MAPA` y se registra `destino_compatibilidad` en el informe.

Este criterio evita excluir páginas sustantivas que usan `canonical` normalmente, porque un `canonical` por sí solo no activa la exclusión.

## Casos de compatibilidad validados

El ajuste cubre específicamente los falsos positivos observados en la Etapa 4:

- `crebeucayali/accesos-complementarios/paginas/mapa-web.html` -> ruta canónica `https://crebeucayali.github.io/accesos-complementarios/mapa-web.html`.
- `crebeucayali/accesos-complementarios/recursos/contacto.html` -> ruta canónica `https://crebeucayali.github.io/accesos-complementarios/paginas/contacto.html`.

Ninguna de estas dos páginas debe convertirse en una entrada independiente del Mapa Web.

## Propuesta de actualización preparada

Se conserva la validación de ocho accesos públicos existentes, creados o ampliados después de la construcción inicial del Mapa Web y ausentes de su estructura actual.

### INICIO

- Buscador EVA: `https://crebeucayali.github.io/buscar/`

### CAP

- Primera jornada: `https://crebeucayali.github.io/capacitaciones/primera-jornada.html`
- Segunda jornada: `https://crebeucayali.github.io/capacitaciones/segunda-jornada.html`

### BDA

- Créditos generales: `https://crebeucayali.github.io/banco-digital-accesible/creditos.html`

### MEA

- Generador LSP con consulta de señas completas y deletreo de respaldo: `https://crebeucayali.github.io/materiales-educativos-accesibles/apoyos-lsp/generador-lsp.html`

### DUA

- Explorador DUA 3.0: `https://crebeucayali.github.io/DUA-3.0/`
- Evolución del DUA: `https://crebeucayali.github.io/DUA-3.0/evolucion.html`
- Centro de recursos DUA: `https://crebeucayali.github.io/DUA-3.0/recursos.html`

Total: 8 accesos.

## Exclusiones preservadas

Se mantienen excluidas:

- `/pruebas/buscador-accesible/`
- `/pruebas/tarjetas-educativas/`
- `/pruebas/generador-por-pasos/`
- cualquier ruta bajo `/pruebas/**` por defecto;
- `admin/`, `docs/`, tests, fixtures, autenticación, activación y archivos auxiliares.

## Reglas editoriales preservadas

- `data-mapa-web="no-publicar"` bloquea publicación.
- `data-mapa-web="publicar"` habilita candidatura, pero no escritura automática.
- HTML nuevo posterior a la línea base sin marca queda `PENDIENTE_CONFIRMACION`.
- HTML existente en la línea base, fuera de exclusiones y sin ser ruta de compatibilidad, se trata como `LEGADO_APROBADO`.
- una redirección de compatibilidad nunca se propone como acceso independiente.

## Resultado de esta etapa

La Etapa 5 deja preparado el verificador para evitar los dos falsos positivos detectados y deja una propuesta exacta de ocho accesos válidos para una futura intervención del Mapa Web.

No se ejecuta todavía esa intervención.

La siguiente etapa deberá modificar únicamente el Mapa Web canónico de manera controlada, incorporando los ocho accesos aprobados y manteniendo las exclusiones definidas.

Estado final: `AJUSTE_VERIFICADOR_Y_PROPUESTA_COMPLETADOS`.
