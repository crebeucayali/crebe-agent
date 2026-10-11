# Directorio de entidades - Etapa 6: mantenimiento periódico

Estado previsto al cierre: `MANTENIMIENTO_PERIODICO_ACTIVO`.

## Objetivo

Convertir el verificador y el mecanismo de propuestas de las etapas anteriores en una supervisión periódica, sin habilitar escritura automática sobre `crebeucayali/accesos-complementarios`.

## Frecuencia

El workflow se programa dos veces al mes, los días 1 y 15 a las 13:00 UTC. Para Perú corresponde a las 08:00 mientras se mantenga UTC-5.

La ejecución manual continúa disponible mediante `workflow_dispatch`.

## Flujo periódico

1. Descargar `crebeucayali/accesos-complementarios` en modo lectura.
2. Ejecutar las pruebas de las etapas 3, 5 y 6.
3. Verificar las 55 entidades actuales y cualquier entidad futura que aparezca en la fuente.
4. Comparar el resultado con `tracking/directorio-entidades-referencia.json`.
5. Detectar altas, bajas, cambios de URL y cambios de estado técnico.
6. Generar propuestas controladas cuando correspondan.
7. Aplicar únicamente aprobaciones válidas a una copia temporal.
8. Generar un diff de revisión.
9. Guardar toda la evidencia como artifact durante 30 días.

## Referencia aprobada

`tracking/directorio-entidades-referencia.json` contiene la fotografía técnica de referencia validada al cierre de la Etapa 5.

La referencia no se actualiza automáticamente. Solo debe cambiar cuando una modificación del directorio haya sido revisada y aprobada. De este modo, un cambio real no se absorbe silenciosamente como nuevo estado normal.

## Cambios relevantes

El informe periódico distingue:

- entidad nueva;
- entidad ausente;
- URL modificada;
- cambio de estado técnico;
- incidencia nueva;
- incidencia resuelta;
- incidencia conocida sin cambios.

Cuando no existen cambios relevantes, el resumen muestra únicamente que el directorio continúa estable y conserva las incidencias conocidas sin repetir innecesariamente todas las propuestas de actualización.

## Seguridad

El workflow conserva:

- `permissions: contents: read`;
- `persist-credentials: false`;
- cero escritura en Supabase;
- cero commit o push automático al repositorio objetivo;
- cero eliminación automática de entidades;
- cero actualización automática de la referencia aprobada.

Las propuestas de modificación continúan sujetas al mecanismo de aprobación exacta de la Etapa 5.

## Entorno de ejecución

La ejecución usa Node.js 24 para evitar depender del runtime Node.js 20 ya deprecado en los runners de GitHub Actions.

## Criterio de cierre

La Etapa 6 queda cerrada cuando:

- el workflow programado queda definido;
- las pruebas de las tres capas pasan;
- la comparación contra la referencia funciona;
- una ejecución real termina correctamente;
- sin cambios en el directorio, el comparador reporta cero cambios relevantes;
- el repositorio objetivo permanece sin modificaciones.
