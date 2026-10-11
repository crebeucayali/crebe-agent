# Directorio de entidades - Etapa 3: verificador solo lectura

Estado final: `VERIFICADOR_LECTURA_FUNCIONAL`.

## Alcance

Se incorpora un verificador real para el Directorio ciudadano de `crebeucayali/accesos-complementarios` sin modificar el repositorio objetivo ni sus datos públicos.

La fuente continúa siendo `directorios/directorio-ciudadano.js`.

## Funcionamiento

1. Lee el archivo de origen desde una copia de solo lectura del repositorio objetivo.
2. Extrae el arreglo `entidades` sin ejecutar el resto del JavaScript del sitio.
3. Genera un identificador técnico estable para seguimiento interno.
4. Comprueba la URL publicada de cada entidad con reintentos controlados.
5. Clasifica el resultado conforme al modelo aprobado en la Etapa 2.
6. Detecta posibles duplicados mediante al menos dos señales, sin decidir eliminación ni fusión.
7. Genera `verificacion.json` e `Informe_directorio_entidades.md` como artefactos de ejecución.

## Estados

El verificador solo puede producir:

- `VERIFICADO`
- `REDIRECCION`
- `ENLACE_ROTO`
- `CAMBIO_DETECTADO`
- `POSIBLE_DUPLICADO`
- `REQUIERE_REVISION`

`CAMBIO_DETECTADO` queda reservado para una etapa posterior de contraste de datos institucionales; esta primera versión se concentra en disponibilidad técnica, redirecciones y posibles duplicados internos.

## Criterios de URL

- Respuesta 2xx/3xx final válida: `VERIFICADO` o `REDIRECCION`.
- 404 o 410: `ENLACE_ROTO`.
- 403 o 429: `REQUIERE_REVISION`, porque puede existir bloqueo a automatización.
- 5xx persistente: `REQUIERE_REVISION`, evitando interpretar una caída temporal como cierre institucional.
- Ausencia de respuesta tras reintentos: `ENLACE_ROTO`, sin eliminar ni desactivar la entidad.
- URL ausente o inválida: `REQUIERE_REVISION`.

## Duplicados

La detección compara nombre normalizado, URL, teléfono, correo, dirección y ámbito. Se exige un mínimo de dos señales y al menos una señal distinta de ámbito. Compartir una única URL o una sigla no basta para declarar duplicidad.

El resultado siempre es `POSIBLE_DUPLICADO`; requiere revisión humana.

## Seguridad

El workflow usa `permissions: contents: read` y ambos `checkout` se ejecutan con `persist-credentials: false`.

No existen pasos de commit, push, edición de archivos del repositorio objetivo, llamadas de escritura a GitHub ni escritura en Supabase.

Los únicos archivos creados durante una ejecución se almacenan en `reports/directorio-entidades/` dentro del entorno temporal de GitHub Actions y se conservan como artefactos.

## Validación ejecutada

Workflow run: `38164383449`.

Resultado: `success`.

Pruebas automáticas: 4 aprobadas, 0 fallidas.

Verificación real inicial:

- entidades revisadas: 55;
- `VERIFICADO`: 13;
- `REDIRECCION`: 2;
- `ENLACE_ROTO`: 4;
- `POSIBLE_DUPLICADO`: 36.

Artefacto generado: `11711791571`, con `verificacion.json` e `Informe_directorio_entidades.md`.

La cantidad elevada de `POSIBLE_DUPLICADO` no se interpreta como 36 duplicados reales. Es una salida preliminar del criterio técnico y debe contrastarse con casos reales en la Etapa 4. No se modifica ningún registro a partir de este resultado.

## Programación

El workflow queda disponible mediante `workflow_dispatch` y también se ejecuta en cambios relacionados con el verificador. No se programa todavía una frecuencia automática; eso corresponde a la Etapa 6.

## Cierre

Se cumplieron los criterios de cierre:

- las pruebas automáticas pasan;
- el workflow ejecutó una verificación real del directorio actual;
- se generó el artefacto con JSON e informe Markdown;
- no se modificó `crebeucayali/accesos-complementarios`;
- no se habilitó ninguna escritura automática.

La Etapa 4 queda habilitada para validar y calibrar los resultados con casos reales.
