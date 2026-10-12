# Fase 9 · Etapa 1 — Auditoría e inventario SEO

## Objetivo

Establecer una línea base técnica de SEO y descubribilidad para los ocho repositorios públicos de EVA antes de aplicar cualquier corrección. La prioridad es reforzar las páginas oficiales publicadas en `https://crebeucayali.github.io/` frente a resultados secundarios, incluidos los repositorios de código en GitHub.

La estrategia es de SEO técnico general y no una variante exclusiva para un navegador. Se consideran Brave Search, Google, Bing y otros motores que interpreten estándares web de rastreo, indexación, canonicalización, sitemaps y datos estructurados.

## Alcance

Repositorios observados:

1. `crebeucayali/crebeucayali.github.io`
2. `crebeucayali/accesos-complementarios`
3. `crebeucayali/capacitaciones`
4. `crebeucayali/banco-digital-accesible`
5. `crebeucayali/materiales-educativos-accesibles`
6. `crebeucayali/noti-inclusivos`
7. `crebeucayali/repositorio-accesible`
8. `crebeucayali/DUA-3.0`

La auditoría inventaría páginas HTML, `title`, `meta description`, `canonical`, `meta robots`, H1, JSON-LD, `robots.txt`, sitemaps y presencia temática de términos institucionales relevantes como inclusión educativa, accesibilidad, discapacidad, diversidad, LSP, Braille, DUA, pictogramas y TEA.

## Hallazgos prioritarios confirmados al iniciar la etapa

- El `sitemap-v2.xml` del portal principal contiene únicamente la portada, por lo que no representa el ecosistema EVA actual.
- Los sitemaps de varios módulos tienen cobertura parcial respecto de las rutas públicas disponibles; DUA 3.0 requiere revisión específica de sitemap.
- Se confirmaron portadas sin `canonical` explícito, entre ellas Accesos Complementarios y Lecturas Inclusivas.
- La portada principal dispone de `og:description`, pero no de `meta name="description"` estándar.
- Los títulos de los módulos no siguen todavía un patrón institucional totalmente uniforme del tipo `[contenido] | CREBE Ucayali`.
- Los `robots.txt` alojados en subrutas se conservan como evidencia de configuración de cada repositorio, pero el control aplicable al host `crebeucayali.github.io` corresponde al `robots.txt` de la raíz.

Estos hallazgos no autorizan correcciones en esta etapa. Sirven para priorizar las etapas siguientes.

## Ejecución reproducible

El agente incorpora:

- `seo_audit.mjs`: auditor de lectura local sobre copias de los ocho repositorios.
- `tests/seo_audit.test.mjs`: pruebas unitarias del extractor SEO.
- `.github/workflows/seo-audit.yml`: workflow manual y de validación por pull request, con `contents: read`.

El workflow clona los ocho repositorios únicamente para lectura, genera `reports/fase-9-etapa-1-auditoria-seo.generated.json`, valida los guardrails y publica el reporte como artifact. Los hallazgos SEO no hacen fallar el workflow: esta etapa diagnostica, no corrige.

## Guardrails

- No modificar repositorios EVA.
- No modificar Supabase.
- No modificar el panel administrativo.
- No forzar indexación ni enviar URLs a motores de búsqueda.
- No alterar contenido, diseño, navegación o funcionalidades.
- No convertir ausencia de una señal SEO en fallo funcional de EVA.

## Criterio de cierre

La Etapa 1 puede cerrarse cuando el auditor:

1. procese los ocho repositorios;
2. genere evidencia reproducible;
3. mantenga todos los guardrails en solo lectura;
4. complete sus pruebas y validación CI;
5. deje priorizados los hallazgos para la Etapa 2.

La Etapa 2, Arquitectura de indexación, permanece fuera de alcance hasta el cierre formal de esta etapa.
