# Directorio de entidades - Etapa 4: validación controlada

Estado final: `VERIFICADOR_VALIDADO`.

## Objetivo

Validar el verificador de solo lectura de la Etapa 3 sobre casos reales y reducir falsos positivos antes de habilitar cualquier mecanismo de actualización.

No se modifica `crebeucayali/accesos-complementarios`, no se cambia ningún dato del Directorio ciudadano y no se habilita escritura automática.

## Hallazgos de la ejecución de Etapa 3

La primera ejecución real procesó 55 entidades y produjo:

- `VERIFICADO`: 13
- `REDIRECCION`: 2
- `ENLACE_ROTO`: 4
- `POSIBLE_DUPLICADO`: 36

La proporción de posibles duplicados fue excesiva. La revisión de casos mostró que muchas coincidencias provenían de valores genéricos compartidos, por ejemplo `Canales oficiales`, `Verificar en canal oficial`, `Atención virtual` o referencias municipales genéricas, además de coincidencias de ámbito. Estos valores no identifican por sí solos a una entidad.

## Calibración de duplicados

Se ajustó el criterio para que una coincidencia de contacto, URL, dirección o ámbito no sea suficiente si los nombres institucionales no son suficientemente similares.

Reglas aplicadas:

1. Los valores genéricos o pendientes de verificación no cuentan como señales de duplicidad.
2. Se exige similitud de nombre igual o superior a 0.75.
3. Si los nombres son similares pero no idénticos, se exige por lo menos una señal fuerte adicional entre URL, teléfono, correo o dirección. El ámbito por sí solo no corrobora duplicidad.
4. Si los nombres son idénticos, igualmente se exige al menos una segunda señal.
5. Compartir únicamente una URL institucional, un ámbito o un canal general no genera `POSIBLE_DUPLICADO`.
6. Una dependencia, programa, oficina regional o servicio que comparte sitio con una entidad mayor no se considera duplicado por ese solo hecho.
7. El resultado continúa siendo únicamente una alerta para revisión humana; nunca autoriza fusión o eliminación.

## Calibración de fallos de red

La Etapa 3 clasificaba una ausencia total de respuesta tras reintentos como `ENLACE_ROTO`.

La validación controlada determinó que un timeout o error de conectividad sin respuesta HTTP definitiva puede deberse a bloqueo automatizado, indisponibilidad temporal, DNS o restricciones de red. Desde esta etapa:

- HTTP 404 o 410 confirmado: `ENLACE_ROTO`.
- HTTP 403, 429 o 5xx persistente: `REQUIERE_REVISION`.
- timeout o error de red persistente sin estado HTTP: `REQUIERE_REVISION`.

Esto evita interpretar una falla técnica temporal como desaparición de una entidad.

## Casos reales revisados

### Observatorio CONADIS

La ejecución anterior agotó los reintentos por timeout. Queda en `REQUIERE_REVISION` y no se declara enlace roto sin una respuesta HTTP definitiva.

### Línea 100

La URL registrada devolvió HTTP 404. El hallazgo corresponde al enlace publicado y no autoriza concluir que el servicio haya desaparecido. No se sustituye la URL en esta etapa.

### Bomberos

La URL registrada devolvió HTTP 404. Se conserva como enlace roto confirmado y posible actualización futura sujeta a aprobación.

### Programa Nacional Warmi Ñan

La URL registrada devolvió HTTP 404. Se conserva como enlace roto confirmado; no se cambia la URL automáticamente.

### Programa Contigo y SUNAT

Ambas rutas producen redirecciones válidas. Se mantienen como `REDIRECCION`; una redirección detectada no reemplaza automáticamente la URL publicada.

## Pruebas ampliadas

La validación final ejecutó 9 pruebas automáticas y todas aprobaron. Se comprobó:

- extracción segura del arreglo de entidades;
- estabilidad del identificador técnico;
- descarte de marcadores genéricos;
- similitud mínima de nombre;
- exigencia de señal fuerte adicional cuando los nombres solo son similares;
- rechazo de candidatos basados únicamente en nombre parecido y mismo ámbito;
- timeout persistente como `REQUIERE_REVISION`;
- 404 confirmado como `ENLACE_ROTO`;
- resumen de estados.

## Resultado de la ejecución validada

Workflow run: `38165375765`.

Entidades revisadas: 55.

- `VERIFICADO`: 49
- `REDIRECCION`: 2
- `ENLACE_ROTO`: 3
- `REQUIERE_REVISION`: 1
- `POSIBLE_DUPLICADO`: 0
- `CAMBIO_DETECTADO`: 0

La calibración redujo las alertas de `POSIBLE_DUPLICADO` de 36 a 0 en el conjunto actual, evitando los falsos positivos identificados durante la validación. Esto no demuestra que nunca puedan existir duplicados futuros; significa que, con los datos actuales, el verificador no dispone de evidencia suficiente para marcar alguno.

## Cierre

La Etapa 4 cumple los criterios definidos:

- 9 de 9 pruebas automáticas aprobadas;
- verificación real de las 55 entidades completada correctamente;
- falsos positivos de duplicados corregidos;
- timeouts separados de 404/410 confirmados;
- workflow conservado en modo de solo lectura;
- `crebeucayali/accesos-complementarios` sin modificaciones;
- Supabase sin modificaciones;
- ninguna actualización, eliminación o fusión automática habilitada.

Estado final: `VERIFICADOR_VALIDADO`.

La Etapa 5 queda habilitada para diseñar y aplicar únicamente el mecanismo de actualización controlada, manteniendo aprobación humana para los cambios institucionales.
