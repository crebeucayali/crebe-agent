# Fase 6 · Etapa 8 — Verificación y monitoreo de integridad

## Objetivo

Cerrar la Fase 6 con una verificación final de solo lectura y dejar un monitoreo recurrente que detecte divergencias futuras en la cadena Panel → Supabase → consulta pública → EVA sin corregir producción automáticamente.

## Verificación final

La verificación profunda del 6 de octubre de 2026 confirmó:

- 152 actividades visibles + 20 capacitaciones visibles = 172 filas en `calendario_publico`;
- 20 capacitaciones visibles = 20 proyecciones en Calendario;
- 0 imágenes hijas huérfanas de Galería;
- 0 eventos persistidos en `eva_visitas_eventos` y `eva_compartidos_eventos`;
- 0 agregados negativos de visitas o compartidos;
- 44 objetos en `eva-publico`;
- 20 objetos Storage únicos referenciados;
- 0 referencias Storage faltantes;
- 24 objetos no referenciados conservados como candidatos a revisión no destructiva.

## Monitor automático

`integrity_monitor.py` utiliza exclusivamente la superficie pública desplegada de EVA.

1. Obtiene `SUPABASE_URL` y la clave publicable desde `capacitaciones/supabase-publico.js` publicado.
2. No persiste ni imprime la clave publicable en el reporte.
3. Ejecuta únicamente consultas REST de lectura.
4. Valida dinámicamente la unión Calendario + Capacitaciones.
5. Comprueba la proyección uno-a-uno de Capacitaciones.
6. Revisa Noticias, Galería y Repositorio publicados.
7. Comprueba que las referencias públicas a `eva-publico` sigan siendo accesibles.
8. Si aparece una divergencia, termina con error y conserva evidencia; no ejecuta correcciones.

## Frecuencia

El workflow `.github/workflows/supabase-integrity-monitor.yml` se ejecuta:

- diariamente a las 11:00 UTC, equivalentes a las 06:00 en `America/Lima`;
- manualmente mediante `workflow_dispatch`;
- en PR cuando cambia el monitor, sus pruebas, el reporte o el tracking de la etapa.

La evidencia runtime se conserva como artefacto durante 30 días.

## Límites deliberados

El monitor diario no ejecuta escrituras de prueba. Por tanto, quedan para auditoría profunda manual:

- semántica de triggers de Visitas y Compartidos;
- RLS y GRANT;
- inventario completo de Storage y los 24 candidatos no referenciados.

Estas exclusiones evitan contaminar métricas reales, introducir service-role en CI o eliminar objetos sin diagnóstico.

## Criterio de alerta

Una alerta del monitor no autoriza una corrección. Debe seguirse la secuencia:

`alerta → reproducción → diagnóstico → autorización → intervención controlada → verificación`

## Estado de cierre

Con la línea base íntegra y el monitor recurrente activo, la Fase 6 pasa a:

`MONITOREO_INTEGRIDAD_ACTIVO`
