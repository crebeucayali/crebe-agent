# Fase 5 — Etapa 8: auditoría recurrente y monitoreo funcional

## Objetivo

Mantener una vigilancia periódica, de solo lectura y de bajo costo sobre los accesos funcionales más importantes de EVA después del cierre de la línea base, diagnóstico, corrección y verificación.

## Diseño

La Etapa 8 no repite diariamente la auditoría completa de 1,297 casos. En su lugar utiliza un conjunto de centinelas públicos que permite detectar caídas, HTTP 404/410, reaparición de referencias obsoletas y pérdida de las correcciones verificadas.

La auditoría completa de la Etapa 3 queda disponible para ejecución manual cuando un centinela genera una alerta, después de cambios relevantes o cuando se requiera reconstruir una nueva línea base.

## Centinelas

Se comprueban diariamente:

- los ocho accesos principales de EVA;
- el contacto institucional vigente;
- la ruta de compatibilidad `/noti-inclusivos/blog/`;
- el índice `/noti-inclusivos/articulos/`;
- las siete páginas de Noti Inclusivos corregidas en la Etapa 6, verificando que no reaparezca la referencia antigua de Contacto.

Total inicial: 18 centinelas.

## Excepción conocida

`F5E4-EAE63AF520` — Juegos Interactivos Accesibles permanece `BLOQUEADO_POR_DECISION_FUNCIONAL`.

Mientras no exista una decisión explícita sobre restitución, retiro o reemplazo del módulo, su URL no se ejecuta como centinela y no debe producir una alerta diaria falsa.

## Frecuencia

El workflow `.github/workflows/functional-monitor.yml` se ejecuta:

- automáticamente todos los días a las 11:00 UTC (06:00, America/Lima);
- manualmente mediante `workflow_dispatch`;
- en pull requests que modifiquen el monitor, su configuración, pruebas, documentación o tracking.

## Seguridad

- `permissions: contents: read`;
- checkout sin credenciales persistentes;
- acciones fijadas por SHA;
- solo solicitudes HTTP GET de lectura;
- no JavaScript de EVA;
- no envío de formularios;
- no autenticación administrativa;
- no Supabase directo;
- no creación automática de issues;
- no corrección automática de repositorios EVA.

## Alertas

Una respuesta inesperada o la pérdida de un marcador funcional hace fallar el job. El informe y el JSON de evidencia se guardan como artefacto durante 30 días.

Una alerta no autoriza una corrección. Debe analizarse antes de intervenir EVA.

## Estado permanente

Una vez validada la primera ejecución, la Etapa 8 no se considera una etapa cerrada tradicional. Su estado estable es:

`MONITOREO_FUNCIONAL_ACTIVO`
