# Directorio de entidades - Etapa 5: actualización controlada

Estado previsto al cierre: `ACTUALIZACION_CONTROLADA_HABILITADA`.

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

## Candidatos controlados de esta etapa

Se incorporan candidatos para los seis hallazgos de la Etapa 4:

- Programa Contigo: conservar la URL actual; la redirección no justifica por sí sola un cambio.
- Línea 100: proponer la orientación oficial vigente en `https://www.gob.pe/479`.
- Bomberos: proponer `https://portal.bomberosperu.gob.pe/`.
- Programa Nacional Warmi Ñan: proponer su sede institucional en gob.pe.
- SUNAT: proponer el portal institucional directo `https://www.sunat.gob.pe/`.
- Observatorio CONADIS: mantener en revisión manual por timeout sin respuesta HTTP definitiva.

Estas referencias son candidatas, no cambios autorizados.

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

## Criterio de cierre

La Etapa 5 puede cerrarse cuando:

- pasan las pruebas del verificador y del mecanismo de aprobación;
- se ejecuta el workflow sobre las 55 entidades reales;
- se generan propuestas controladas;
- con el manifiesto de aprobaciones vacío se aplican cero cambios;
- el archivo público permanece intacto;
- las propuestas que requieren modificación quedan pendientes de aprobación explícita.

El resultado final del workflow se registrará en `tracking/directorio-entidades-etapa-5.json`.
