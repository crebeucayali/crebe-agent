# Mapa Web - Etapa 2: modelo de publicación y transición

Estado: MODELO_PUBLICACION_APROBADO

## Alcance

Este modelo se aplica al mantenimiento del Mapa Web canónico de EVA ubicado actualmente en `crebeucayali/accesos-complementarios/mapa-web.html`.

La Etapa 2 no modifica `mapa-web.html`, no añade DUA todavía, no inserta marcas en las páginas actuales y no habilita escrituras automáticas sobre ningún repositorio EVA. Solo define las reglas que deberá seguir el verificador de la Etapa 3.

## Objetivo

Evitar que el agente incorpore al Mapa Web páginas, rutas o secciones creadas para pruebas, experimentación, desarrollo temporal o navegación interna.

La existencia técnica de un archivo HTML o de una sección no significa que deba publicarse en el Mapa Web.

## Marca explícita de publicación

Para páginas completas se utilizará el atributo `data-mapa-web` en el elemento `body`.

Página autorizada para incorporarse al Mapa Web:

```html
<body data-mapa-web="publicar">
```

Página que debe excluirse del Mapa Web:

```html
<body data-mapa-web="no-publicar">
```

Para una sección navegable concreta dentro de una página:

```html
<section id="identificador-estable" data-mapa-web="publicar">
```

Para una sección que no debe aparecer:

```html
<section id="identificador-estable" data-mapa-web="no-publicar">
```

La marca solo expresa intención editorial. No sustituye las verificaciones técnicas del agente.

## Estados permitidos

El agente deberá clasificar cada página o sección candidata con uno de estos estados:

- `PUBLICAR_EN_MAPA`: existe autorización explícita mediante `data-mapa-web="publicar"` y la ruta cumple las verificaciones técnicas.
- `NO_PUBLICAR_EN_MAPA`: existe `data-mapa-web="no-publicar"` o la ruta pertenece a una exclusión técnica inequívoca.
- `PENDIENTE_CONFIRMACION`: no existe marca suficiente o hay ambigüedad sobre si el recurso debe incorporarse.
- `YA_REGISTRADO`: el recurso autorizado ya existe correctamente en el Mapa Web.
- `CAMBIO_DETECTADO`: el recurso ya registrado presenta cambio de ruta, título o ubicación que debe revisarse.
- `RUTA_NO_DISPONIBLE`: una ruta registrada en el Mapa Web ya no responde o no puede validarse.

Ninguno de estos estados autoriza modificación automática durante las Etapas 2, 3 o 4.

## Regla principal de seguridad

La ausencia de marca nunca equivale a autorización.

Una página o sección nueva sin `data-mapa-web` deberá quedar como `PENDIENTE_CONFIRMACION` y no podrá incorporarse automáticamente.

## Exclusiones técnicas

Aunque una página contenga `data-mapa-web="publicar"`, el agente deberá detenerse y marcar revisión si pertenece a un contexto que normalmente no debe publicarse en el mapa, como:

- `admin/`
- `tests/` o carpetas equivalentes de pruebas
- `.github/`
- `docs/`
- fixtures
- páginas de autenticación o activación
- archivos temporales
- prototipos claramente identificados como prueba
- recursos no navegables como CSS, JS, JSON, imágenes o archivos auxiliares

La marca no debe utilizarse para saltarse controles de seguridad.

## Requisitos mínimos para una página publicable

Para clasificar una página como `PUBLICAR_EN_MAPA`, la Etapa 3 deberá comprobar como mínimo:

1. `data-mapa-web="publicar"` en `body`.
2. Ruta pública válida.
3. Página accesible desde el despliegue previsto.
4. Título visible o título documental utilizable.
5. No pertenecer a las exclusiones técnicas.
6. No duplicar otra ruta canónica ya registrada.
7. Poder determinar a qué módulo o grupo del Mapa Web pertenece.

Si falta cualquiera de estos criterios, el resultado será `PENDIENTE_CONFIRMACION` o el estado técnico que corresponda.

## Requisitos mínimos para una sección publicable

Una sección interna solo será candidata si:

1. tiene `data-mapa-web="publicar"`;
2. dispone de un `id` estable;
3. tiene un encabezado visible significativo;
4. representa una unidad navegable real y no una división meramente decorativa;
5. pertenece a una página pública válida;
6. su ancla puede expresarse mediante una URL estable, por ejemplo `pagina.html#seccion`.

Una sección sin `id` o sin encabezado significativo no deberá incorporarse automáticamente.

## Política de transición para páginas existentes

En la Etapa 1 se comprobó que las páginas actuales de EVA todavía no utilizan `data-mapa-web`.

Para evitar que todo el ecosistema pase artificialmente a `PENDIENTE_CONFIRMACION`, se utilizará una transición controlada:

- las rutas ya existentes en `mapa-web.html` se considerarán `LEGADO_APROBADO` para fines de comparación;
- `LEGADO_APROBADO` es una condición interna de transición, no una nueva marca HTML;
- una ruta ya incluida en el mapa no necesita recibir inmediatamente `data-mapa-web="publicar"` para seguir existiendo;
- las nuevas páginas o secciones creadas después de activar el sistema sí deberán usar la marca o requerir confirmación;
- el agente no insertará marcas de forma masiva en páginas existentes durante las Etapas 2 o 3.

## Tratamiento de recursos actuales no incluidos

Si el agente encuentra una ruta pública existente que no está en `mapa-web.html` y tampoco tiene marca:

- no la incorporará;
- la clasificará como `PENDIENTE_CONFIRMACION`;
- mostrará evidencia de dónde fue detectada;
- solicitará decisión editorial.

Esto aplica también al caso actualmente observado de DUA 3.0: su existencia pública no autoriza todavía una modificación del Mapa Web dentro de esta etapa.

## Fuentes de evidencia

La Etapa 3 podrá comparar, en modo de solo lectura:

- `mapa-web.html` como inventario publicado actual;
- páginas HTML de los repositorios EVA;
- navegación visible de portadas y módulos;
- `sitemap.xml` cuando exista;
- enlaces públicos entre módulos;
- marcas `data-mapa-web` cuando empiecen a utilizarse.

El `sitemap.xml` será evidencia auxiliar y nunca la única fuente de decisión.

## Prioridad entre señales

Orden de prioridad recomendado:

1. `data-mapa-web="no-publicar"` bloquea publicación.
2. Exclusión técnica inequívoca bloquea publicación automática.
3. `data-mapa-web="publicar"` habilita candidatura, pero exige validación técnica.
4. Ruta ya existente en el mapa se trata como legado aprobado.
5. Ruta nueva sin marca queda pendiente de confirmación.

## Acciones prohibidas en esta etapa

- modificar `mapa-web.html`;
- añadir o retirar módulos del mapa;
- insertar marcas `data-mapa-web` en páginas actuales;
- eliminar rutas porque ya no respondan;
- modificar sitemaps;
- modificar Supabase;
- realizar commits en repositorios EVA distintos de `crebe-agent`;
- convertir automáticamente un hallazgo en publicación.

## Resultado exigido para la Etapa 3

El verificador de solo lectura deberá producir por candidato, como mínimo:

```json
{
  "repositorio": "crebeucayali/ejemplo",
  "ruta": "/ejemplo.html",
  "tipo": "pagina",
  "marca": "publicar",
  "estado": "PUBLICAR_EN_MAPA",
  "titulo": "Ejemplo",
  "grupo_mapa": "AC",
  "ya_en_mapa": false,
  "fuente_deteccion": "navegacion",
  "observacion": "..."
}
```

Para secciones deberá registrar además el `id` y la URL con ancla.

## Criterio de cierre

La Etapa 2 queda cerrada cuando:

- la marca `data-mapa-web` está definida;
- los estados de clasificación están definidos;
- la ausencia de marca queda bloqueada como publicación automática;
- la política de transición para páginas existentes está definida;
- las exclusiones técnicas están definidas;
- los requisitos de páginas y secciones publicables están definidos;
- el formato mínimo de salida de la Etapa 3 está definido;
- no se ha modificado ningún repositorio EVA productivo.

Estado final: `MODELO_PUBLICACION_APROBADO`.
