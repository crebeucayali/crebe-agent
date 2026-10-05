# Fase 5, Etapa 2: casos de prueba y resultados esperados

## Objetivo

Transformar el inventario funcional de la Etapa 1 en un contrato de prueba trazable. Cada elemento inventariado conserva un caso con identificador estable, acción a realizar, resultado esperado, evidencia requerida, prioridad y política de ejecución.

## Alcance

La Etapa 2 trabaja únicamente en `crebeucayali/crebe-agent`. No modifica ninguno de los ocho repositorios EVA y no ejecuta acciones funcionales sobre las páginas.

Se generan casos para navegación, enlaces externos, anclas, recursos embebidos, formularios, controles, botones, correo, teléfono y JavaScript inline cuando existe en el inventario.

## Prioridad

- `P0_CRITICA`: acciones administrativas o potencialmente persistentes que requieren especial control.
- `P1_ALTA`: formularios, botones, recursos y funciones principales.
- `P2_MEDIA`: navegación interna o externa relevante.
- `P3_BAJA`: anclas, correo, teléfono y controles de menor impacto.

La prioridad define el orden futuro de ejecución. No significa que exista un fallo.

## Política de ejecución

- `SESION_CONTROLADA_DATOS_PRUEBA`: funciones administrativas con posible persistencia.
- `DATOS_PRUEBA_CONTROLADOS`: formularios públicos o auxiliares que pueden enviar información.
- `AUTOMATIZABLE_LECTURA`: navegación y carga de recursos sin efectos laterales.
- `LECTURA_SIN_EFECTOS_EXTERNOS`: enlaces externos limitados a comprobaciones seguras.
- `NAVEGADOR_INSTRUMENTADO_SIN_PERSISTENCIA`: botones y controles cuya respuesta debe observarse sin alterar datos.
- `MANUAL_O_INSTRUMENTADA`: correo, teléfono o acciones que dependen del entorno del dispositivo.

## Criterios de cierre

La etapa puede cerrarse cuando:

1. Cada elemento funcional de la Etapa 1 tiene exactamente un caso de prueba.
2. No existen identificadores duplicados.
3. Los ocho repositorios están representados.
4. Todos los casos tienen acción, resultado esperado, evidencia requerida, prioridad y política de ejecución.
5. Las pruebas automatizadas del generador son satisfactorias.
6. El workflow finaliza correctamente.
7. No se modifica ninguno de los ocho repositorios EVA.

## Límites

Esta etapa no pulsa botones, no navega por las páginas, no envía formularios, no ejecuta JavaScript de EVA y no consulta ni modifica Supabase. Los casos permanecen en `DEFINIDO_NO_EJECUTADO`.

La Etapa 3 será la primera auditoría funcional ejecutada y utilizará estos casos para clasificar resultados como `CORRECTO`, `FALLO_CONFIRMADO`, `REQUIERE_VERIFICACION_MANUAL`, `NO_APLICA` o `BLOQUEADO_POR_DEPENDENCIA`.
