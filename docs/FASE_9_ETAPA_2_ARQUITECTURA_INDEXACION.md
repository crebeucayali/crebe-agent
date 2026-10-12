# Fase 9 — Etapa 2: Arquitectura de indexación

## Objetivo

Centralizar el descubrimiento de las URLs oficiales de EVA mediante una arquitectura de sitemaps coherente para Brave Search, Google, Bing y otros rastreadores compatibles con los estándares web.

## Alcance aplicado

- El `robots.txt` efectivo del host raíz se conserva sin cambios y continúa declarando `https://crebeucayali.github.io/sitemap-v2.xml`.
- `sitemap-v2.xml` pasa a ser un índice central de sitemaps.
- Se crea `sitemap-main.xml` para la portada y el buscador público de EVA.
- Se completan los sitemaps de Accesos Complementarios, Capacitaciones, Banco Digital Accesible, Materiales Educativos Accesibles y Lecturas Inclusivas.
- Se crea el sitemap de DUA 3.0.
- Repositorio Accesible conserva su sitemap existente porque ya representa su única página HTML pública estable.

La arquitectura resultante contiene ocho sitemaps hijos y 56 URLs oficiales previstas.

## Exclusiones deliberadas

No se incluyen archivos de verificación de buscadores, administración `noindex`, rutas bajo `/pruebas/`, redirecciones o rutas de compatibilidad, plantillas técnicas o dinámicas sin URL estable y duplicados cuyo destino preferente ya está representado por otra URL.

En particular, se excluyen la ruta histórica `accesos-complementarios/paginas/mapa-web.html`, la redirección `recursos/contacto.html`, `banco-digital-accesible/biblioteca/recurso.html`, referencias técnicas bajo `docs/referencias/` y `noti-inclusivos/blog/`, cuya canonical apunta al archivo `/articulos/`.

## Criterio sobre `lastmod`

No se inventan fechas de modificación. La Etapa 2 utiliza sitemaps mínimos con `loc` cuando no existe una fuente fiable y mantenida para `lastmod`. Esta decisión evita enviar señales temporales imprecisas a los buscadores.

## Repositorios intervenidos

Se modificaron únicamente archivos de sitemap en siete repositorios EVA. No se modificaron HTML, CSS, JavaScript, Supabase, panel administrativo ni contenido visible.

PRs de producto:

- `crebeucayali.github.io` PR #20
- `accesos-complementarios` PR #9
- `capacitaciones` PR #4
- `banco-digital-accesible` PR #4
- `materiales-educativos-accesibles` PR #6
- `noti-inclusivos` PR #6
- `DUA-3.0` PR #4

## Verificación

`seo_indexation_verify.mjs` comprueba en modo de solo lectura que:

- `robots.txt` declara el índice central;
- el índice central contiene exactamente ocho sitemaps;
- cada sitemap contiene exactamente las URLs aprobadas para esta etapa;
- no existen URLs duplicadas entre sitemaps;
- todas las URLs pertenecen a `https://crebeucayali.github.io/`;
- cada URL corresponde a un archivo fuente existente;
- ninguna ruta excluida aparece en los sitemaps.

La Etapa 3 — Canonical y metadata — permanece fuera de alcance y no se inicia en esta intervención.
