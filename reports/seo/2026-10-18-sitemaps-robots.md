# Auditoría controlada SEO: sitemaps y robots (2026-10-18)

## Alcance y evidencia
- Repositorio principal `crebeucayali/crebeucayali.github.io`: lectura directa en rama predeterminada de `sitemap.xml`, `sitemap-v2.xml`, `sitemap-main.xml` y `robots.txt`.
- Lectura directa de `sitemap.xml` en siete repositorios: `accesos-complementarios`, `capacitaciones`, `banco-digital-accesible`, `materiales-educativos-accesibles`, `noti-inclusivos`, `repositorio-accesible`, `DUA-3.0`.
- Search Console: captura aportada por responsable muestra ambos sitemaps enviados, con "No se ha podido obtener", tipo "Desconocido" y 0 páginas descubiertas. Fechas de envío: 2026-08-05 (sitemap.xml) y 2026-09-10 (sitemap-v2.xml).
- La comprobación HTTP de las URL públicas no pudo realizarse desde las herramientas de este entorno. **No interpretar la imposibilidad de consulta como HTTP 404 ni como bloqueo de Google**.

## Resultados de inventario
| Fuente | Tipo | URL declaradas |
|---|---|---:|
| /sitemap.xml | urlset | 1 |
| /sitemap-main.xml | urlset | 2 |
| /sitemap-v2.xml | sitemapindex | 8 sitemaps |
| accesos-complementarios/sitemap.xml | urlset | 15 |
| capacitaciones/sitemap.xml | urlset | 3 |
| banco-digital-accesible/sitemap.xml | urlset | 12 |
| materiales-educativos-accesibles/sitemap.xml | urlset | 11 |
| noti-inclusivos/sitemap.xml | urlset | 9 |
| repositorio-accesible/sitemap.xml | urlset | 1 |
| DUA-3.0/sitemap.xml | urlset | 3 |

El índice v2 referencia el sitemap principal y siete sitemaps secundarios: 56 URL declaradas en conjunto, **no verificadas aún como accesibles, canónicas o indexables**. El sitemap legacy declara solo la portada y se solapa con el índice v2.
El robots principal actual: `User-agent: *`, `Allow: /` y `Sitemap: https://crebeucayali.github.io/sitemap-v2.xml`. No se observa una prohibición global.

## Hallazgos y decisiones
1. **ALTO / lectura Search Console fallida:** ambos sitemaps figuran no obtenibles. Causa raíz aún sin demostrar; no atribuir automáticamente a XML ni a falta de URL internas. Antes de cambios de producción verificar desde red externa status HTTP, redirecciones, Content-Type, documento servido en GitHub Pages, robots e informes detallados de cada sitemap en Search Console.
2. **MEDIO / entrada duplicada:** `sitemap.xml` contiene solo la portada; `sitemap-v2.xml` ya incluye un índice de ocho fuentes. Recomendación condicionada: mantener el índice v2 como fuente canónica y, una vez confirmada su lectura, decidir sobre el envío legacy; no eliminarlo ciegamente.
3. **MEDIO / cobertura indexable no verificada:** 56 URL declaradas, entre ellas galerías, herramientas y portales; validar cada ruta (200, canonical, robots/meta robots, contenido estable y útil, ausencia de duplicidad/redirección) antes de ampliar o eliminar URL.
4. **BAJO / rastreo robots:** `robots.txt` principal coherente y con sitemap anunciado. No cambiar directivas sin evidencia; recordar que robots no sirve para prohibir indexación de páginas privadas.
5. **MEDIO / observabilidad:** crear comprobación reproducible en agente de archivos XML (well-formed), índice->hijos, coincidencia de hosts y duplicados; añadir prueba de publicación HTTP separada cuando haya salida de red y evaluar Search Console tras reenviar.

## Plan de subsanación ordenado
- P1: Inspección HTTP reproducible desde equipo/red con acceso: cada archivo raíz y los ocho secundarios. Registrar status, URL final, MIME, XML parseable, contenido servido, fecha y headers, sin cambios de código.
- P2: Abrir cada detalle de sitemap en Search Console y registrar error exacto/última lectura. Resolver rutas o publicación solo si falla inspección; no confundir un error histórico de Search Console con ausencia actual del archivo.
- P3: Verificar lista canónica de 56 URL y registrar faltantes prioritarios con pruebas; aplicar solo correcciones a rutas reales.
- P4: Cuando todas las pruebas pasen, reenviar `sitemap-v2.xml` y observar estado de lectura y páginas descubiertas. Revisar necesidad de conservar/remover la entrada legacy en Search Console.
- P5: Incorporar al agente auditoría periódica de sitemap, robots y rutas públicas, separando diagnóstico de cambios autorizados.

## Estado
**AUDITORÍA ESTÁTICA COMPLETADA / VALIDACIÓN HTTP Y SEARCH CONSOLE PENDIENTE.**
Sin cambios en sitemaps, robots, GitHub Pages, Supabase, autenticación o el resto de repositorios EVA. No se declara la incidencia resuelta ni se crea commit de despliegue sin prueba de causa.
