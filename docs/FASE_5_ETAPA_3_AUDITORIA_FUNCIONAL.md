# Fase 5, Etapa 3: auditoría funcional inicial

Objetivo: ejecutar de manera controlada los casos definidos en la Etapa 2 y establecer una línea base funcional de EVA sin modificar los ocho repositorios ni producir efectos persistentes.

## Alcance

La ejecución automática se limita a casos cuya política permite lectura segura:

- `AUTOMATIZABLE_LECTURA`
- `LECTURA_SIN_EFECTOS_EXTERNOS`

Las comprobaciones internas usan solicitudes HTTP de lectura sin ejecutar JavaScript. Los enlaces externos se verifican mediante `HEAD` y, cuando el servidor no lo admite, mediante una lectura mínima.

Los casos con políticas que requieren navegador, datos de prueba o sesión administrativa no se fuerzan contra producción. Se clasifican como `REQUIERE_VERIFICACION_MANUAL` o `BLOQUEADO_POR_DEPENDENCIA` según corresponda.

## Estados

- `CORRECTO`: la comprobación permitida por la política produjo el resultado esperado en modo lectura.
- `FALLO_CONFIRMADO`: existe evidencia concluyente de fallo, por ejemplo 404/410 o un ancla interna inexistente.
- `REQUIERE_VERIFICACION_MANUAL`: el comportamiento necesita interacción instrumentada o revisión humana para observarse sin riesgo.
- `NO_APLICA`: el caso no contiene una condición comprobable bajo su definición actual.
- `BLOQUEADO_POR_DEPENDENCIA`: la prueba depende de autenticación, datos controlados, permisos, limitaciones de red o respuesta del servicio externo.

`REQUIERE_VERIFICACION_MANUAL` y `BLOQUEADO_POR_DEPENDENCIA` no significan fallo.

## Seguridad operativa

La Etapa 3 no:

- modifica archivos de los ocho repositorios EVA;
- ejecuta JavaScript de EVA;
- pulsa botones mediante navegador;
- envía formularios;
- inicia sesión;
- utiliza credenciales administrativas;
- consulta o modifica Supabase directamente;
- crea, modifica o elimina contenido institucional.

## Salidas

- `reports/functional-audit/functional-audit.json`
- `reports/functional-audit/Informe_fase_5_etapa_3.md`

Cada resultado conserva el ID del caso de la Etapa 2, repositorio, página, prioridad, política, estado de auditoría, detalle y evidencia disponible.

## Criterio de cierre

La Etapa 3 puede cerrarse cuando:

1. se procesen los 1,297 casos definidos por la Etapa 2;
2. cada caso termine en uno de los cinco estados autorizados;
3. las verificaciones automáticas se limiten a operaciones de lectura segura;
4. los hallazgos confirmados queden identificados sin iniciar correcciones;
5. las pruebas automatizadas y el workflow finalicen correctamente;
6. ninguno de los ocho repositorios EVA sea modificado;
7. la Etapa 4 permanezca sin iniciar.

El cierre de esta etapa no significa que todos los casos hayan sido ejecutados de forma interactiva. Significa que toda la matriz ha sido procesada y que los casos no seguros para automatización han quedado explícitamente separados para revisión posterior.
