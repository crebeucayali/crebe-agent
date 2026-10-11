# Directorio de entidades - Etapa 4: validación controlada

Estado previsto al cierre: `VERIFICADOR_VALIDADO`.

## Objetivo

Validar el verificador de solo lectura de la Etapa 3 sobre casos reales y reducir falsos positivos antes de habilitar cualquier mecanismo de actualización.

No se modifica `crebeucayali/accesos-complementarios`, no se cambia ningún dato del Directorio ciudadano y no se habilita escritura automática.

## Hallazgos de la ejecución de Etapa 3

La primera ejecución real procesó 55 entidades y produjo:

- `VERIFICADO`: 13
- `REDIRECCION`: 2
- `ENLACE_ROTO`: 4
- `POSIBLE_DUPLICADO`: 36

La proporción de posibles duplicados fue excesiva. La revisión de casos mostró que muchas coincidencias provenían de valores genéricos compartidos, por ejemplo `Canales oficiales`, `Verificar en canal oficial` o `Atención virtual`, además de coincidencias de ámbito. Estos valores no identifican a una entidad y no deben usarse como evidencia de duplicidad.

## Calibración de duplicados

Se ajusta el criterio para que una coincidencia de contacto, URL, dirección o ámbito no sea suficiente si los nombres institucionales no son suficientemente similares.

Reglas aplicadas:

1. Los valores genéricos o pendientes de verificación no cuentan como señales de duplicidad.
2. Se exige similitud de nombre igual o superior a 0.75.
3. Además del nombre similar, debe existir por lo menos otra señal coincidente entre URL, teléfono, correo, dirección o ámbito.
4. Compartir únicamente una URL institucional, un ámbito o un canal general no genera `POSIBLE_DUPLICADO`.
5. Una dependencia, programa, oficina regional o servicio que comparte sitio con una entidad mayor no se considera duplicado por ese solo hecho.
6. El resultado continúa siendo únicamente una alerta para revisión humana; nunca autoriza fusión o eliminación.

## Calibración de fallos de red

La Etapa 3 clasificaba una ausencia total de respuesta tras reintentos como `ENLACE_ROTO`.

La validación controlada determina que un timeout o error de conectividad sin respuesta HTTP definitiva puede deberse a bloqueo automatizado, indisponibilidad temporal, DNS o restricciones de red. Por seguridad, desde esta etapa:

- HTTP 404 o 410 confirmado: `ENLACE_ROTO`.
- HTTP 403, 429 o 5xx persistente: `REQUIERE_REVISION`.
- timeout o error de red persistente sin estado HTTP: `REQUIERE_REVISION`.

Esto evita interpretar una falla técnica temporal como desaparición de una entidad.

## Casos reales revisados

### Observatorio CONADIS

La ejecución anterior agotó los reintentos por timeout. Se conserva para revisión y ya no se clasifica automáticamente como enlace roto sin respuesta HTTP definitiva.

### Línea 100

La URL registrada devolvió HTTP 404. El servicio continúa existiendo dentro de la red de servicios del MIMP/Warmi Ñan, por lo que el hallazgo corresponde al enlace publicado y no a la desaparición del servicio. No se sustituye la URL en esta etapa.

### Bomberos

La URL registrada en `gob.pe` devolvió HTTP 404, mientras existe un portal institucional activo del Cuerpo General de Bomberos Voluntarios del Perú. Se conserva como enlace roto confirmado y posible actualización futura sujeta a aprobación.

### Programa Nacional Warmi Ñan

La URL registrada devolvió HTTP 404 y existen servicios institucionales activos bajo dominios de Warmi Ñan. Se conserva como enlace roto confirmado; no se cambia la URL automáticamente.

### Programa Contigo y SUNAT

Ambas rutas produjeron redirecciones válidas en la Etapa 3. Se mantienen como `REDIRECCION`; una redirección detectada no reemplaza automáticamente la URL publicada.

## Pruebas añadidas

Se amplían las pruebas para comprobar:

- descarte de marcadores genéricos;
- similitud mínima de nombre;
- rechazo de falsos duplicados por contactos compartidos;
- timeout persistente como `REQUIERE_REVISION`;
- 404 confirmado como `ENLACE_ROTO`;
- conservación de extracción, IDs y resumen de estados.

## Criterio de cierre

La Etapa 4 queda cerrada cuando:

- las pruebas ampliadas pasan;
- el workflow ejecuta nuevamente las 55 entidades reales;
- el número de falsos posibles duplicados disminuye de forma sustancial;
- los timeouts quedan separados de los enlaces 404/410 confirmados;
- se conserva el modo de solo lectura;
- no se modifica `crebeucayali/accesos-complementarios`.

El recuento final se documentará después de la ejecución validada del workflow.
