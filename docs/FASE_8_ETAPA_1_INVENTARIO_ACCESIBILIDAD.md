# Fase 8 — Etapa 1: Inventario de accesibilidad

Estado: `ETAPA_1_COMPLETADA_INVENTARIO_ACCESIBILIDAD`

## Objetivo

Definir el universo y las superficies de accesibilidad que serán auditadas en EVA antes de asignar incumplimientos, severidades o correcciones.

## Alcance

La fase cubre los ocho repositorios EVA y toma como universo base validado 65 páginas HTML y 1,297 elementos funcionales. También conserva el desglose funcional existente: 196 botones, 18 formularios, 175 controles, 711 enlaces de navegación, 110 enlaces externos, 74 anclas, 13 enlaces de correo y 54 referencias JavaScript.

## Superficies inventariadas

1. Imágenes y texto alternativo.
2. Botones, enlaces y nombres accesibles.
3. Formularios, labels, errores y ayuda.
4. Encabezados y jerarquía semántica.
5. Idioma y títulos de documento.
6. Landmarks y regiones.
7. Navegación por teclado.
8. Foco visible y orden de foco.
9. Modales, diálogos y contenido dinámico.
10. ARIA: roles, estados y propiedades.
11. Tablas y relaciones semánticas.
12. Contraste, alto contraste y uso del color.
13. Zoom, reflujo, tamaño de texto y comportamiento móvil.
14. Multimedia y componentes administrativos.

## Regla de esta etapa

Esta etapa es exclusivamente de inventario. No se considera que una superficie tenga un defecto por el solo hecho de existir. Los incumplimientos deberán demostrarse posteriormente mediante evidencia reproducible.

Por ello, en esta etapa:

- no se modifica ningún repositorio EVA;
- no se asigna severidad;
- no se corrige HTML, CSS o JavaScript;
- no se declaran imágenes sin `alt`, errores de contraste o fallos ARIA sin verificación;
- no se inicia automáticamente la Etapa 2.

## Resultado

- Repositorios: 8.
- Páginas HTML: 65.
- Elementos funcionales: 1,297.
- Superficies de accesibilidad: 14.
- Hallazgos confirmados: 0.
- Correcciones aplicadas: 0.

La siguiente etapa, cuando sea autorizada, deberá convertir estas superficies en contratos y criterios verificables de accesibilidad antes de ejecutar la línea base.
