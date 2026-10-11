# Directorio de entidades - Etapa 2: modelo de verificación

Estado: MODELO_VERIFICACION_APROBADO

## Alcance

Este modelo se aplica únicamente al Directorio ciudadano de `crebeucayali/accesos-complementarios`, cuya fuente actual es `directorios/directorio-ciudadano.js`.

No modifica el directorio público, no migra datos a Supabase, no altera categorías, no elimina entidades y no habilita escrituras automáticas.

## Identificación lógica

Cada entidad deberá disponer, cuando se implemente el verificador, de un identificador técnico estable separado de `sigla`, porque las siglas actuales no son únicas.

Formato previsto:

- `id`: identificador estable generado a partir del nombre normalizado y, si fuera necesario, un sufijo diferenciador.
- `nombre`: nombre publicado de la entidad.
- `sigla`: sigla actual, sin utilizarla como clave primaria.

El identificador se utilizará para seguimiento interno del agente y no obliga a modificar todavía la estructura pública.

## Campos de origen

El agente debe leer sin reinterpretar los 11 campos actuales:

- `nombre`
- `sigla`
- `categoria`
- `ambito`
- `servicio`
- `direccion`
- `telefono`
- `correo`
- `horario`
- `web`
- `observacion`

## Metadatos de verificación

La Etapa 3 podrá generar, fuera del directorio público, estos metadatos:

- `id`
- `estado_verificacion`
- `ultima_verificacion`
- `http_status`
- `url_final`
- `tipo_cambio`
- `nivel_confianza`
- `observacion_verificacion`

Estos metadatos no se mezclarán todavía con el archivo público.

## Estados permitidos

Solo se utilizarán estos estados:

- `VERIFICADO`: el recurso consultado responde y no existe evidencia suficiente de cambio relevante.
- `REDIRECCION`: la URL responde mediante redirección a otra URL.
- `ENLACE_ROTO`: no existe respuesta válida después de los reintentos controlados o existe error definitivo de acceso.
- `CAMBIO_DETECTADO`: existe evidencia concreta de que algún dato publicado podría haber cambiado.
- `POSIBLE_DUPLICADO`: dos o más registros presentan coincidencias suficientes para requerir revisión humana.
- `REQUIERE_REVISION`: el agente no dispone de evidencia suficiente para decidir.

No se crearán estados adicionales durante la primera implementación salvo necesidad técnica documentada.

## Reglas de clasificación

### VERIFICADO

Se asigna cuando la URL oficial responde correctamente y no se detecta una discrepancia verificable con los datos publicados.

No significa que todos los datos institucionales hayan sido certificados como vigentes; significa que el control automatizado no detectó una incidencia.

### REDIRECCION

Se asigna cuando la URL publicada termina en otra URL mediante redirección HTTP o equivalente.

La redirección no autoriza por sí sola a sustituir la URL publicada.

### ENLACE_ROTO

Se asigna únicamente después de descartar un fallo transitorio mediante reintentos controlados.

Un timeout aislado, error temporal 5xx o caída puntual no permite eliminar ni desactivar una entidad.

### CAMBIO_DETECTADO

Se utiliza cuando existe evidencia verificable de una posible actualización de URL, nombre, teléfono, correo, dirección, horario u otro dato publicado.

El agente documentará el valor actual, el valor observado y la fuente de evidencia.

### POSIBLE_DUPLICADO

No se decidirá por coincidencia de nombre solamente.

La detección deberá ponderar al menos dos señales entre nombre normalizado, URL, teléfono, correo, dirección y ámbito. Una coincidencia de URL compartida por entidades dependientes no constituye automáticamente duplicado.

### REQUIERE_REVISION

Se utiliza cuando existe conflicto entre fuentes, falta evidencia, el sitio oficial es ambiguo o la entidad depende de otra institución y comparte canales generales.

## Reglas de seguridad y control

1. El agente no eliminará entidades automáticamente.
2. El agente no cambiará automáticamente nombre institucional, teléfono, correo, dirección, categoría, ámbito, servicio, horario ni observación.
3. Una URL nueva detectada se propondrá, pero no se aplicará en esta fase.
4. Una redirección no se convertirá automáticamente en reemplazo permanente.
5. Los errores temporales deberán reintentarse antes de clasificarse como enlace roto.
6. Las fuentes oficiales tendrán prioridad sobre directorios de terceros, redes sociales no oficiales y agregadores.
7. Si dos fuentes oficiales discrepan, el resultado será `REQUIERE_REVISION`.
8. La ausencia de un dato en una página oficial no implica que el dato publicado sea falso.
9. El agente no inferirá cierre institucional únicamente por un sitio caído.
10. Toda propuesta futura deberá conservar trazabilidad: entidad, dato anterior, dato propuesto, evidencia y fecha.

## Política de duplicados

La primera implementación debe diferenciar:

- entidad realmente duplicada;
- dependencia regional de una entidad nacional;
- programa o servicio perteneciente a una entidad mayor;
- varias entidades que comparten la misma página de `gob.pe`;
- registros con siglas iguales pero instituciones distintas.

Por ello, `sigla` y `web` nunca serán criterios únicos para decidir duplicidad.

## Categorías

Se conserva el conjunto detectado en la Etapa 1 sin modificarlo:

- Educación
- Discapacidad e inclusión
- Salud
- Protección y familia
- Gobierno y trámites
- Justicia y trabajo
- Emergencias
- Ayuda social
- Cultura e interculturalidad

La diferencia existente entre estas categorías y las opciones visibles del selector HTML queda registrada como hallazgo, pero no se corrige dentro de esta etapa.

## Niveles de confianza

El verificador podrá expresar confianza interna con tres niveles:

- `ALTA`: evidencia directa en fuente oficial y coincidencia inequívoca.
- `MEDIA`: evidencia razonable, pero requiere confirmación humana antes de modificar datos.
- `BAJA`: información incompleta, ambigua o contradictoria.

Ningún nivel de confianza autoriza escritura automática durante las Etapas 2, 3 o 4.

## Resultado exigido para la Etapa 3

El verificador de solo lectura deberá producir por entidad, como mínimo:

```json
{
  "id": "...",
  "nombre": "...",
  "estado_verificacion": "VERIFICADO",
  "ultima_verificacion": "YYYY-MM-DDTHH:MM:SSZ",
  "http_status": 200,
  "url_original": "...",
  "url_final": "...",
  "tipo_cambio": null,
  "nivel_confianza": "ALTA",
  "observacion_verificacion": "..."
}
```

## Criterio de cierre

La Etapa 2 queda cerrada cuando:

- el conjunto de estados está definido;
- las reglas de clasificación están definidas;
- la política de duplicados está definida;
- las reglas de no modificación están definidas;
- el formato de salida de la Etapa 3 está definido;
- no se ha alterado ningún archivo de `accesos-complementarios`.

Estado final: `MODELO_VERIFICACION_APROBADO`.
