# Mapa Web - Etapa 3: verificador de solo lectura

Estado: VERIFICADOR_SOLO_LECTURA_IMPLEMENTADO

## Alcance

La Etapa 3 implementa en `crebeucayali/crebe-agent` un verificador de solo lectura para comparar el Mapa Web canónico de EVA con las páginas HTML existentes en los ocho repositorios supervisados.

No modifica `mapa-web.html`, no inserta marcas en páginas EVA, no modifica Supabase, no elimina rutas y no realiza commits en repositorios productivos.

## Criterio editorial confirmado antes de esta etapa

Después del cierre de la Etapa 2 se verificó el caso especial del repositorio principal y se confirmó el criterio operativo para la línea base:

- todos los accesos HTML públicos que ya existen en los repositorios EVA al activar la Etapa 3 se consideran válidos como `LEGADO_APROBADO`, siempre que no pertenezcan a una exclusión técnica;
- las rutas bajo `/pruebas/` del repositorio principal no son publicables;
- las nuevas páginas creadas después de esta línea base requieren `data-mapa-web="publicar"` o quedan como `PENDIENTE_CONFIRMACION`;
- `data-mapa-web="no-publicar"` siempre bloquea la publicación;
- se mantienen las exclusiones técnicas de administración, documentación, pruebas, fixtures, autenticación, activación y recursos no navegables.

Este criterio evita tener que marcar manualmente todas las páginas existentes y, al mismo tiempo, impide que una página futura de prueba se incorpore por el solo hecho de existir.

## Exclusiones verificadas del repositorio principal

Se registran explícitamente como no publicables:

1. `pruebas/buscador-accesible/index.html`: ruta antigua de compatibilidad que redirige al buscador definitivo y declara `noindex`.
2. `pruebas/tarjetas-educativas/index.html`: herramienta identificada como ruta experimental.
3. `pruebas/generador-por-pasos/`: referencia obsoleta de prototipo detectada en el índice de búsqueda; no existe actualmente como ruta activa.

Además, cualquier nueva ruta situada bajo `pruebas/` queda excluida por defecto.

## Línea base inmutable

La Etapa 3 incorpora `tracking/mapa-web-baseline.json` con el commit exacto de cada repositorio en el momento de activación.

Esta decisión es necesaria para diferenciar:

- página existente antes del agente: `LEGADO_APROBADO`;
- página creada después de activar el agente: requiere marca o confirmación.

El verificador compara el árbol HTML de cada commit de línea base contra el árbol actual de `main`. La línea base no debe desplazarse automáticamente, porque hacerlo convertiría páginas nuevas en legado sin revisión.

## Repositorios supervisados

- `crebeucayali/crebeucayali.github.io` -> `INICIO`
- `crebeucayali/accesos-complementarios` -> `AC`
- `crebeucayali/capacitaciones` -> `CAP`
- `crebeucayali/banco-digital-accesible` -> `BDA`
- `crebeucayali/materiales-educativos-accesibles` -> `MEA`
- `crebeucayali/noti-inclusivos` -> `NI`
- `crebeucayali/repositorio-accesible` -> `RA`
- `crebeucayali/DUA-3.0` -> `DUA`

## Verificador

Archivo:

```text
mapa_web_verify.py
```

Funciones principales:

1. lee la línea base aprobada;
2. obtiene el árbol HTML actual y el árbol correspondiente al commit de línea base de cada repositorio;
3. lee el `mapa-web.html` canónico;
4. normaliza rutas de GitHub Pages, incluyendo `index.html`;
5. aplica exclusiones técnicas antes de considerar una ruta publicable;
6. interpreta `data-mapa-web` cuando exista;
7. detecta secciones marcadas, comprobando `id` y encabezado visible;
8. compara cada candidato con los enlaces ya presentes en el Mapa Web;
9. genera un informe JSON local sin escribir en los repositorios EVA.

## Clasificación aplicada

### `NO_PUBLICAR_EN_MAPA`

Se utiliza cuando:

- existe `data-mapa-web="no-publicar"`;
- la ruta pertenece a `/pruebas/`;
- pertenece a otra exclusión técnica inequívoca.

### `YA_REGISTRADO`

La ruta está presente en el Mapa Web y continúa existiendo en un repositorio supervisado.

### `PUBLICAR_EN_MAPA`

Se utiliza para:

- una ruta de la línea base que es `LEGADO_APROBADO`, no está excluida y todavía no aparece en el mapa;
- una ruta posterior a la línea base con `data-mapa-web="publicar"` que cumple los controles técnicos;
- una sección marcada para publicar con `id` estable y encabezado visible.

Este estado significa "candidata válida". No modifica el Mapa Web automáticamente.

### `PENDIENTE_CONFIRMACION`

Se utiliza para una ruta creada después de la línea base que no tiene una marca editorial suficiente o para una sección marcada de forma incompleta.

### `RUTA_NO_DISPONIBLE`

Se informa cuando una URL del Mapa Web no puede asociarse con una página HTML actual dentro de los repositorios supervisados. El agente no la elimina.

## Formato del resultado

Por candidato se conserva, como mínimo:

```json
{
  "repositorio": "crebeucayali/ejemplo",
  "ruta": "/ejemplo.html",
  "url": "https://crebeucayali.github.io/ejemplo/ejemplo.html",
  "tipo": "pagina",
  "marca": null,
  "estado": "PUBLICAR_EN_MAPA",
  "titulo": "Ejemplo",
  "grupo_mapa": "AC",
  "ya_en_mapa": false,
  "fuente_deteccion": "baseline+arbol_actual",
  "legado_aprobado": true,
  "observacion": "..."
}
```

Las secciones añaden `id_seccion` y una URL con ancla.

## Ejecución

```bash
python mapa_web_verify.py
```

Salida predeterminada:

```text
reports/mapa-web-etapa-3.json
```

La comprobación HTTP es opcional y no altera por sí sola la decisión editorial:

```bash
python mapa_web_verify.py --check-http
```

Puede utilizar `GITHUB_TOKEN` o `GH_TOKEN` para ampliar el límite de lectura de la API de GitHub. No requiere permisos de escritura.

## Seguridad

El verificador no contiene operaciones `PUT`, `PATCH`, `POST` ni `DELETE` contra los repositorios EVA. Solo consulta ramas, commits, árboles, HTML público y el Mapa Web.

El archivo de salida se crea únicamente en el entorno donde se ejecuta el agente. La Etapa 3 no contiene ninguna rutina para abrir PR, fusionar cambios o modificar el mapa.

## Criterio de cierre

La Etapa 3 se considera implementada cuando:

- existe una línea base fija para los ocho repositorios;
- `/pruebas/` y las exclusiones verificadas quedan bloqueadas;
- el verificador diferencia legado, páginas nuevas y marcas editoriales;
- el Mapa Web puede compararse contra las rutas reales;
- se detectan secciones marcadas sin publicar automáticamente;
- se genera un informe JSON trazable;
- no se modifica ningún repositorio EVA productivo.

Estado final: `VERIFICADOR_SOLO_LECTURA_IMPLEMENTADO`.

La Etapa 4 deberá ejecutar y validar el verificador sobre el estado real de EVA, revisar falsos positivos y ajustar criterios antes de permitir cualquier propuesta de cambio al Mapa Web.
