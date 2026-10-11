# Directorio de entidades - Etapa 5: actualización controlada

Estado final: `ACTUALIZACION_CONTROLADA_HABILITADA`.

## Objetivo

Incorporar un mecanismo que transforme hallazgos validados en propuestas concretas sin modificar automáticamente `crebeucayali/accesos-complementarios`.

La Etapa 5 mantiene separación estricta entre diagnóstico, propuesta, aprobación y aplicación.

## Flujo

1. El verificador revisa el Directorio ciudadano en modo lectura.
2. Un catálogo controlado aporta candidatos de URL para hallazgos conocidos.
3. Cada URL candidata se vuelve a verificar antes de convertirse en propuesta.
4. Las propuestas válidas quedan como `PENDIENTE_APROBACION` y reciben una huella inmutable.
5. El archivo `config/directorio-entidades-aprobaciones.json` inicia vacío.
6. Solo una aprobación con `id`, `valor_nuevo` y `huella` exactamente coincidentes puede generar un cambio.
7. Incluso con aprobación, el workflow solo genera una copia temporal y un diff; no hace commit ni push al repositorio objetivo.

## Acciones posibles

- `ACTUALIZAR_URL`: candidato técnicamente válido, requiere aprobación.
- `MANTENER_URL`: el registro actual funciona y no conviene cambiarlo automáticamente.
- `REVISAR_MANUALMENTE`: no existe evidencia técnica suficiente para proponer sustitución.

## Resultado validado

El workflow `38166438507` terminó correctamente sobre las 55 entidades reales.

Pruebas aprobadas:

- verificador: 9/9;
- actualización controlada: 6/6;
- total: 15/15.

Se procesaron los seis hallazgos no verificados de la Etapa 4 y el resultado fue:

- `ACTUALIZAR_URL`: 4;
- `MANTENER_URL`: 1;
- `REVISAR_MANUALMENTE`: 1.

Las cuatro propuestas de actualización quedaron pendientes de aprobación explícita:

- Línea 100: `https://www.gob.pe/linea100` → `https://www.gob.pe/479`;
- Bomberos: `https://www.gob.pe/bomberos` → `https://portal.bomberosperu.gob.pe/`;
- Programa Nacional Warmi Ñan: `https://www.gob.pe/warminan` → `https://www.gob.pe/institucion/warmi%C3%B1an/institucional`;
- SUNAT: `https://www.gob.pe/sunat` → `https://www.sunat.gob.pe/`.

Programa Contigo quedó en `MANTENER_URL` porque su dirección actual funciona y una redirección válida no justifica por sí sola una modificación.

Observatorio CONADIS quedó en `REVISAR_MANUALMENTE` por timeout sin una respuesta HTTP definitiva.

Con el manifiesto de aprobaciones vacío, el mecanismo registró `aprobaciones_validas: 0`, aplicó cero cambios y generó un diff de 0 bytes. Por tanto, el directorio público permaneció intacto.

## Protección contra aprobaciones obsoletas

Cada propuesta de actualización genera una huella SHA-256 corta a partir de:

- identificador técnico;
- acción;
- valor actual;
- valor nuevo.

Si cualquiera de estos valores cambia, la huella deja de coincidir y la aprobación es rechazada. Esto evita aplicar una autorización antigua sobre una propuesta diferente.

## Archivos incorporados

- `directory_entities_proposals.mjs`
- `directory_entities_apply_approved.mjs`
- `config/directorio-entidades-candidatos.json`
- `config/directorio-entidades-aprobaciones.json`
- `tests/directory_entities_stage5.test.mjs`
- `.github/workflows/directory-entities-controlled-update.yml`

## Seguridad

El workflow conserva `permissions: contents: read` y `persist-credentials: false`.

No contiene pasos de commit, push, creación de PR en `accesos-complementarios`, escritura en Supabase ni eliminación de entidades.

La salida de aplicación es exclusivamente:

`reports/directorio-entidades/directorio-ciudadano.propuesto.js`

junto con un diff de revisión:

`reports/directorio-entidades/cambios-aprobados.patch`

## Cierre

La Etapa 5 queda cerrada con el mecanismo de actualización controlada habilitado y validado. No se ha autorizado todavía ninguna de las cuatro modificaciones propuestas al Directorio ciudadano.

La Etapa 6 queda habilitada para incorporar el mantenimiento periódico, manteniendo las mismas restricciones de aprobación para cambios institucionales.
